#!/usr/bin/env python3
"""FoxxDesk validation/preflight.

V5 CI is validation-only: it never reapplies branding, rewrites workflows, installs
image dependencies or replaces hbb_common during a build. The prepared source is
committed first; CI proves that the committed tree is coherent before compilation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

SCRIPT_VERSION = 'foxxdesk-validate-v6-submodule-safe-2026-09-05'
sys.path.insert(0, str(Path(__file__).resolve().parent))
from foxxdesk_config import CONFIG_REL, load_config  # noqa: E402


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='ignore')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def same_file(a: Path, b: Path) -> bool:
    return a.is_file() and b.is_file() and digest(a) == digest(b)


def dependency_compatibility(root: Path, cfg: dict) -> list[str]:
    scripts_dir = str(root / 'scripts')
    sys.path.insert(0, scripts_dir)
    try:
        import foxxdesk_sync_hbb_common as sync  # type: ignore
        errors = list(sync.compatibility_errors(root))
        try:
            expected, source = sync.expected_commit(root, cfg)
            current = sync.current_hbb_commit(root)
            if current is None:
                # A vendored/copied tree can be API-compatible without .git metadata.
                # In CI with a real submodule, current should normally be available.
                pass
            elif current != expected:
                errors.append(f'revisão {current} != {expected} ({source})')
        except Exception as exc:
            errors.append(f'não foi possível determinar a revisão esperada: {exc}')
        return errors
    finally:
        try:
            sys.path.remove(scripts_dir)
        except ValueError:
            pass


def xml_string_value(text: str, name: str) -> Optional[str]:
    m = re.search(
        rf'<string\b[^>]*\bname\s*=\s*["\']{re.escape(name)}["\'][^>]*>\s*([^<]+?)\s*</string\s*>',
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return m.group(1).strip() if m else None


def android_application_label(manifest: str) -> Optional[str]:
    # Search only the opening <application ...> tag, not activity/service labels.
    m = re.search(r'<application\b([^>]*)>', manifest, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    a = re.search(r'android:label\s*=\s*["\']([^"\']+)["\']', m.group(1), flags=re.IGNORECASE)
    return a.group(1).strip() if a else None


def xcconfig_value(text: str, key: str) -> Optional[str]:
    m = re.search(rf'(?m)^\s*{re.escape(key)}\s*=\s*(.*?)\s*$', text)
    if not m:
        return None
    return m.group(1).strip().strip('"\'')


def rc_string_value(text: str, key: str) -> Optional[str]:
    m = re.search(
        rf'VALUE\s+["\']{re.escape(key)}["\']\s*,\s*["\']([^"\']*)["\']',
        text,
        flags=re.IGNORECASE,
    )
    return m.group(1).rstrip('\\0').strip() if m else None


def validate_public_brand(root: Path, display: str) -> tuple[list[str], list[str]]:
    """Semantic platform checks that tolerate upstream formatting changes."""
    errors: list[str] = []
    warnings: list[str] = []

    strings_path = root / 'flutter/android/app/src/main/res/values/strings.xml'
    strings_value: Optional[str] = None
    if strings_path.is_file():
        strings_value = xml_string_value(read(strings_path), 'app_name')
        if strings_value is None:
            warnings.append(f'Android app_name: string app_name não encontrada em {strings_path.relative_to(root)}')
        elif strings_value != display:
            errors.append(f'Android app_name = {strings_value!r}, esperado {display!r}')

    manifest_path = root / 'flutter/android/app/src/main/AndroidManifest.xml'
    if manifest_path.is_file():
        label = android_application_label(read(manifest_path))
        if label is None:
            warnings.append(f'Android manifest: android:label da aplicação não encontrado em {manifest_path.relative_to(root)}')
        elif label == '@string/app_name':
            if strings_value is not None and strings_value != display:
                errors.append(f'Android manifest usa @string/app_name, mas app_name = {strings_value!r}, esperado {display!r}')
        elif label != display:
            errors.append(f'Android application label = {label!r}, esperado {display!r} ou @string/app_name')

    mac_path = root / 'flutter/macos/Runner/Configs/AppInfo.xcconfig'
    if mac_path.is_file():
        value = xcconfig_value(read(mac_path), 'PRODUCT_NAME')
        if value is None:
            warnings.append(f'macOS product name: PRODUCT_NAME não encontrado em {mac_path.relative_to(root)}')
        elif value != display:
            errors.append(f'macOS PRODUCT_NAME = {value!r}, esperado {display!r}')

    win_path = root / 'flutter/windows/runner/Runner.rc'
    if win_path.is_file():
        value = rc_string_value(read(win_path), 'ProductName')
        if value is None:
            warnings.append(f'Windows ProductName: campo ProductName não encontrado em {win_path.relative_to(root)}')
        elif value != display:
            errors.append(f'Windows ProductName = {value!r}, esperado {display!r}')

    return errors, warnings


def validate_icon_cache(root: Path, source: Path, *, strict: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    state_path = root / '.foxxdesk/icon-state.json'
    manifest_path = root / '.foxxdesk/icon-overlay-manifest.json'
    overlay_root = root / '.foxxdesk/icon-overlay'

    if not state_path.is_file():
        (errors if strict else warnings).append('icon-state.json ausente; rode foxxdesk_prepare.py localmente e faça commit')
        return errors, warnings

    try:
        state = json.loads(state_path.read_text(encoding='utf-8'))
        expected = str(state.get('master_sha256', '')).lower()
        current = digest(source)
        if not expected or expected != current:
            errors.append('icon-state.json não corresponde ao ícone mestre atual; rode foxxdesk_prepare.py')
    except Exception as exc:
        errors.append(f'icon-state.json inválido: {exc}')
        return errors, warnings

    if not manifest_path.is_file():
        (errors if strict else warnings).append('icon-overlay-manifest.json ausente; rode foxxdesk_prepare.py localmente e faça commit')
        return errors, warnings

    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        files = manifest.get('files', [])
        if not isinstance(files, list) or not files:
            errors.append('icon-overlay-manifest.json não contém lista de assets')
            return errors, warnings
        mismatches: list[str] = []
        for rel in files:
            if not isinstance(rel, str) or not rel:
                continue
            cached = overlay_root / rel
            actual = root / rel
            if not cached.is_file():
                mismatches.append(f'{rel} (cache ausente)')
            elif not actual.is_file():
                mismatches.append(f'{rel} (asset ausente)')
            elif not same_file(cached, actual):
                mismatches.append(f'{rel} (asset != cache)')
        if mismatches:
            preview = ', '.join(mismatches[:8])
            extra = f' (+{len(mismatches)-8})' if len(mismatches) > 8 else ''
            errors.append(f'cache determinístico de ícones divergente: {preview}{extra}; rode foxxdesk_prepare.py e faça commit')
    except Exception as exc:
        errors.append(f'icon-overlay-manifest.json inválido: {exc}')

    return errors, warnings


def main() -> int:
    p = argparse.ArgumentParser(description='Valida configuração, brand, ícones e compatibilidade FoxxDesk')
    p.add_argument('--target', default='.')
    p.add_argument('--ci', action='store_true', help='Preflight estrito e somente leitura para GitHub Actions')
    args = p.parse_args()
    root = Path(args.target).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    try:
        cfg, migrated = load_config(root, migrate_legacy=True, write_migration=False)
    except Exception as exc:
        print(f'ERRO: configuração inválida em {CONFIG_REL}: {exc}', file=sys.stderr)
        return 2

    if migrated:
        warnings.append('brand.json contém valores legados; commit o foxxdesk.config.json atualizado')

    brand = cfg['brand']
    network = cfg['network']
    icons = cfg['icons']
    display = str(brand['display_name'])
    slug = str(brand['slug'])

    cargo = root / 'Cargo.toml'
    if cargo.is_file():
        cargo_text = read(cargo)
        if not re.search(rf'(?m)^name\s*=\s*"{re.escape(slug)}"\s*$', cargo_text):
            errors.append(f'Cargo.toml: package principal não está como {slug}')
    else:
        errors.append('Cargo.toml ausente')

    # hbb_common is an upstream submodule in V6. Brand/server/key defaults must
    # live in the parent crate, never in submodule files.
    hbb_cfg = root / 'libs/hbb_common/src/config.rs'
    if not hbb_cfg.is_file():
        errors.append('libs/hbb_common/src/config.rs ausente')
    else:
        hbb_text = read(hbb_cfg)
        legacy_markers = [
            'DEFAULT_RENDEZVOUS_SERVER',
            'DEFAULT_RELAY_SERVER',
            'DEFAULT_CUSTOM_CLIENT_KEY',
            'RwLock::new("FoxxDesk".to_owned())',
        ]
        if any(marker in hbb_text for marker in legacy_markers):
            errors.append('hbb_common contém branding FoxxDesk legado; rode o prepare para restaurar o submódulo upstream')

    runtime = subprocess.run(
        [sys.executable, str(root / 'scripts/foxxdesk_runtime_defaults.py'), '--target', str(root), '--check'],
        cwd=str(root), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if runtime.returncode != 0:
        errors.append('defaults runtime FoxxDesk ausentes/desatualizados: ' + (runtime.stderr.strip() or runtime.stdout.strip()))

    brand_errors, brand_warnings = validate_public_brand(root, display)
    errors.extend(brand_errors)
    warnings.extend(brand_warnings)

    if icons.get('enabled', True):
        source = root / str(icons.get('source', '.foxxdesk/assets/icon.png'))
        if not source.is_file():
            errors.append(f'ícone mestre ausente: {source.relative_to(root)}')
        else:
            res_icon = root / 'res/icon.png'
            if not same_file(source, res_icon):
                errors.append('res/icon.png não corresponde ao ícone mestre configurado')
            icon_errors, icon_warnings = validate_icon_cache(root, source, strict=args.ci)
            errors.extend(icon_errors)
            warnings.extend(icon_warnings)

    errors.extend(f'hbb_common: {e}' for e in dependency_compatibility(root, cfg))

    own_wf = root / '.github/workflows/foxxdesk-build.yml'
    if own_wf.is_file():
        own = read(own_wf)
        if 'workflow_dispatch:' not in own:
            errors.append('foxxdesk-build.yml: workflow_dispatch ausente')
        if re.search(r'(?m)^\s{2}(push|pull_request|schedule)\s*:', own):
            errors.append('foxxdesk-build.yml: gatilho automático proibido detectado')
    else:
        errors.append('workflow FoxxDesk manual ausente: .github/workflows/foxxdesk-build.yml')

    helpers = [
        'scripts/foxxdesk_config.py',
        'scripts/apply_foxxdesk_rebrand.py',
        'scripts/apply_foxxdesk_icon.py',
        'scripts/foxxdesk_sync_hbb_common.py',
        'scripts/foxxdesk_ci_hooks.py',
        'scripts/foxxdesk_prepare.py',
        'scripts/foxxdesk_validate.py',
        'scripts/foxxdesk_runtime_defaults.py',
    ]
    for rel in helpers:
        path = root / rel
        if not path.is_file():
            errors.append(f'helper ausente: {rel}')
            continue
        cp = subprocess.run(
            [sys.executable, '-m', 'py_compile', str(path)], cwd=str(root),
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if cp.returncode != 0:
            errors.append(f'helper Python inválido {rel}: {cp.stderr.strip()}')

    hooks = subprocess.run(
        [sys.executable, str(root / 'scripts/foxxdesk_ci_hooks.py'), '--target', str(root), '--check'],
        cwd=str(root), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if hooks.returncode != 0:
        errors.append('layout de GitHub Actions inconsistente: ' + (hooks.stderr.strip() or hooks.stdout.strip()))

    if args.ci and (root / '.git').exists():
        dirty = subprocess.run(
            ['git', 'status', '--porcelain', '--untracked-files=no', '--', 'libs/hbb_common'],
            cwd=str(root), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if dirty.returncode == 0 and dirty.stdout.strip():
            errors.append('libs/hbb_common está modificado no checkout; o submódulo deve permanecer upstream/limpo na V6')

    for item in warnings:
        print(f'AVISO: {item}')
    if errors:
        print('\nPRECHECK FALHOU:', file=sys.stderr)
        for item in errors:
            print(f' - {item}', file=sys.stderr)
        if args.ci:
            print(
                '\nCI é somente leitura. Corrija localmente com:\n'
                '  python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps\n'
                'depois faça commit/push das alterações antes de executar o build.',
                file=sys.stderr,
            )
        return 2

    mode = 'CI read-only' if args.ci else 'local'
    print(f'FoxxDesk validation OK ({SCRIPT_VERSION}, {mode})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
