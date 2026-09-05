#!/usr/bin/env python3
"""Fast FoxxDesk preflight for CI and local updates."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_VERSION = 'foxxdesk-validate-v2-config-safe-2026-09-04'
sys.path.insert(0, str(Path(__file__).resolve().parent))
from foxxdesk_config import CONFIG_REL, load_config  # noqa: E402


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='ignore')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def same_file(a: Path, b: Path) -> bool:
    return a.is_file() and b.is_file() and digest(a) == digest(b)


def dependency_compatibility(root: Path, cfg: dict) -> list[str]:
    sys.path.insert(0, str(root / 'scripts'))
    try:
        import foxxdesk_sync_hbb_common as sync  # type: ignore
        errors = list(sync.compatibility_errors(root))
        try:
            expected, source = sync.expected_commit(root, cfg)
            current = sync.current_hbb_commit(root)
            if current is not None and current != expected:
                errors.append(f'revisão {current} != {expected} ({source})')
        except Exception as exc:
            errors.append(f'não foi possível determinar a revisão esperada: {exc}')
        return errors
    finally:
        try:
            sys.path.remove(str(root / 'scripts'))
        except ValueError:
            pass


def main() -> int:
    p = argparse.ArgumentParser(description='Valida configuração, brand, ícones e compatibilidade FoxxDesk')
    p.add_argument('--target', default='.')
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
        warnings.append('brand.json ainda contém valores usados apenas para migração; commit o foxxdesk.config.json atualizado e remova o legado quando conveniente')

    brand = cfg['brand']
    network = cfg['network']
    icons = cfg['icons']
    display = str(brand['display_name'])
    slug = str(brand['slug'])
    server = str(network['server'])
    relay = str(network.get('relay') or server)
    key = str(network['key'])

    cargo = root / 'Cargo.toml'
    if cargo.is_file():
        cargo_text = read(cargo)
        if not re.search(rf'(?m)^name\s*=\s*"{re.escape(slug)}"\s*$', cargo_text):
            errors.append(f'Cargo.toml: package principal não está como {slug}')
    else:
        errors.append('Cargo.toml ausente')

    hbb_cfg = root / 'libs/hbb_common/src/config.rs'
    if hbb_cfg.is_file():
        text = read(hbb_cfg)
        invariants = [
            (f'RwLock::new("{display}".to_owned())', 'APP_NAME'),
            (f'pub const DEFAULT_RENDEZVOUS_SERVER: &str = "{server}";', 'servidor padrão'),
            (f'pub const DEFAULT_RELAY_SERVER: &str = "{relay}";', 'relay padrão'),
            (f'pub const DEFAULT_CUSTOM_CLIENT_KEY: &str = "{key}";', 'chave pública padrão'),
        ]
        for needle, label in invariants:
            if needle not in text:
                errors.append(f'hbb_common config: {label} não aplicado')
    else:
        errors.append('libs/hbb_common/src/config.rs ausente')

    optional_invariants = [
        (root / 'flutter/android/app/src/main/res/values/strings.xml', f'>{display}<', 'Android app_name'),
        (root / 'flutter/android/app/src/main/AndroidManifest.xml', f'android:label="{display}"', 'Android manifest'),
        (root / 'flutter/macos/Runner/Configs/AppInfo.xcconfig', f'PRODUCT_NAME = {display}', 'macOS product name'),
        (root / 'flutter/windows/runner/Runner.rc', f'VALUE "ProductName", "{display}"', 'Windows ProductName'),
    ]
    for path, needle, label in optional_invariants:
        if path.exists() and needle not in read(path):
            # Safe profile intentionally avoids rewriting every optional UI file.
            # Warn rather than fail unless a bootstrap/full run is expected.
            warnings.append(f'{label}: brand não encontrado em {path.relative_to(root)}')

    if icons.get('enabled', True):
        source = root / str(icons.get('source', '.foxxdesk/assets/icon.png'))
        if not source.is_file():
            errors.append(f'ícone mestre ausente: {source.relative_to(root)}')
        else:
            res_icon = root / 'res/icon.png'
            if not same_file(source, res_icon):
                errors.append('res/icon.png não corresponde ao ícone mestre configurado')
            state_path = root / '.foxxdesk/icon-state.json'
            if state_path.is_file():
                try:
                    state = json.loads(state_path.read_text(encoding='utf-8'))
                    expected = str(state.get('master_sha256', '')).lower()
                    current = digest(source)
                    if expected and expected != current:
                        errors.append('icon-state.json não corresponde ao ícone mestre atual; rode foxxdesk_prepare.py')
                except Exception as exc:
                    errors.append(f'icon-state.json inválido: {exc}')
            else:
                warnings.append('icon-state.json ausente; o próximo prepare irá criá-lo')

    errors.extend(f'hbb_common: {e}' for e in dependency_compatibility(root, cfg))

    helpers = [
        'scripts/foxxdesk_config.py',
        'scripts/apply_foxxdesk_rebrand.py',
        'scripts/apply_foxxdesk_icon.py',
        'scripts/foxxdesk_sync_hbb_common.py',
        'scripts/foxxdesk_ci_hooks.py',
        'scripts/foxxdesk_prepare.py',
        'scripts/foxxdesk_validate.py',
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
        errors.append('hooks de GitHub Actions ausentes: ' + (hooks.stderr.strip() or hooks.stdout.strip()))

    for item in warnings:
        print(f'AVISO: {item}')
    if errors:
        print('\nPRECHECK FALHOU:', file=sys.stderr)
        for item in errors:
            print(f' - {item}', file=sys.stderr)
        return 2

    print(f'FoxxDesk validation OK ({SCRIPT_VERSION})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
