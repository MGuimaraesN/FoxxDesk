#!/usr/bin/env python3
"""Deterministic FoxxDesk updater/build preparer.

Design rules:
- one config: .foxxdesk/foxxdesk.config.json
- one visual source: icons.source (normally .foxxdesk/assets/icon.png)
- hbb_common is synced to the matching RustDesk revision before branding
- runtime rebrand is the normal local update mode; full is explicit bootstrap/audit
- icon assets are regenerated from the master source, not restored blindly from
  an old snapshot; the overlay is only an optional cache/fallback
- missing master icon can be safely seeded locally from a fallback only when its
  SHA-256 matches the last committed icon state; CI itself is read-only
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_VERSION = "foxxdesk-prepare-v9-build-safe-2026-09-06"
STATE_REL = Path('.foxxdesk/icon-state.json')
OVERLAY_MANIFEST_REL = Path('.foxxdesk/icon-overlay-manifest.json')

sys.path.insert(0, str(Path(__file__).resolve().parent))
from foxxdesk_config import CONFIG_REL, OPTIONAL_BRAND_ASSETS, load_config  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_state(root: Path) -> dict[str, Any]:
    path = root / STATE_REL
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def copy_if_changed(src: Path, dst: Path) -> bool:
    if not src.is_file():
        raise FileNotFoundError(f"Fonte ausente: {src}")
    if dst.is_file() and sha256(src) == sha256(dst):
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def resolve_master_icon(root: Path, cfg: dict[str, Any], *, apply: bool) -> tuple[Path, bool]:
    icons = cfg['icons']
    source_rel = Path(str(icons.get('source', '.foxxdesk/assets/icon.png')))
    source = root / source_rel
    if source.is_file():
        return source, False

    if not bool(icons.get('auto_seed_missing_source', True)):
        raise FileNotFoundError(f"Fonte ausente: {source}")

    state = load_state(root)
    expected_hash = str(state.get('master_sha256', '')).strip().lower()
    allow_unverified = bool(cfg.get('safety', {}).get('allow_unverified_icon_fallback', False))
    rejected: list[str] = []
    for rel in icons.get('fallback_sources', ['res/icon.png']):
        candidate = root / str(rel)
        if not candidate.is_file():
            continue
        candidate_hash = sha256(candidate)
        if expected_hash and candidate_hash != expected_hash:
            rejected.append(f"{rel} (sha256 {candidate_hash[:12]} != esperado {expected_hash[:12]})")
            continue
        if not expected_hash and not allow_unverified:
            rejected.append(f"{rel} (sem icon-state para confirmar que é o ícone FoxxDesk)")
            continue
        if apply:
            source.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidate, source)
            print(f"[icons] fonte mestre ausente; restaurada com segurança de {rel}")
            return source, True
        print(f"[icons] dry-run: usaria fallback seguro {rel} para {source_rel}")
        return candidate, False

    details = '; '.join(rejected) if rejected else 'nenhum fallback existente'
    raise FileNotFoundError(
        f"Fonte ausente: {source}. Não foi possível restaurá-la com segurança ({details}). "
        f"Garanta que {source_rel} esteja commitado no Git ou restaure o ícone FoxxDesk correto."
    )


def pillow_available() -> bool:
    return importlib.util.find_spec('PIL') is not None


def restore_overlay_cache(root: Path, master: Path) -> int:
    state = load_state(root)
    expected = str(state.get('master_sha256', '')).strip().lower()
    current = sha256(master)
    if not expected or expected != current:
        raise RuntimeError(
            "Pillow não está disponível e o cache de ícones não corresponde ao ícone mestre atual. "
            "Instale Pillow (python3 -m pip install Pillow) e rode novamente o prepare local."
        )
    manifest_path = root / OVERLAY_MANIFEST_REL
    if not manifest_path.is_file():
        raise RuntimeError("Pillow não está disponível e o cache .foxxdesk/icon-overlay não existe")
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    changed = 0
    restore_files = list(manifest.get('files', [])) + list(manifest.get('optional_files', []))
    for rel in restore_files:
        rel_path = Path(rel)
        src = root / '.foxxdesk/icon-overlay' / rel_path
        dst = root / rel_path
        if not src.is_file():
            continue
        changed += int(copy_if_changed(src, dst))
    changed += int(copy_if_changed(master, root / 'res/icon.png'))
    return changed


def generator_target_paths(generator: Path, *, include_ios_contents: bool = False) -> list[str]:
    spec = importlib.util.spec_from_file_location('foxxdesk_icon_generator', generator)
    if not spec or not spec.loader:
        return []
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    paths = [x['path'] for x in module.ALL_IMAGE_ASSETS]
    paths += [x['path'] for x in module.SVG_ASSETS]
    paths += [x['path'] for x in module.ICO_ASSETS]
    paths += [x['path'] for x in module.ICNS_ASSETS]
    if include_ios_contents and hasattr(module, 'EXPECTED_CONTENTS_JSON_PATH'):
        paths += [module.EXPECTED_CONTENTS_JSON_PATH]
    return sorted(set(paths))


def refresh_overlay_and_state(root: Path, cfg: dict[str, Any], master: Path) -> None:
    generator = root / 'scripts/apply_foxxdesk_icon.py'
    required_files: list[str] = []
    optional_files: list[str] = []
    include_ios_contents = bool(cfg['icons'].get('update_ios_contents', False))
    for rel in generator_target_paths(generator, include_ios_contents=include_ios_contents) + ['res/icon.png']:
        src = root / rel
        if not src.is_file():
            continue
        dst = root / '.foxxdesk/icon-overlay' / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        if rel in OPTIONAL_BRAND_ASSETS:
            optional_files.append(rel)
        else:
            required_files.append(rel)
    (root / OVERLAY_MANIFEST_REL).write_text(
        json.dumps({
            'schema': 3,
            'files': sorted(set(required_files)),
            'optional_files': sorted(set(optional_files)),
        }, indent=2, ensure_ascii=False) + '\n',
        encoding='utf-8',
    )
    icon_cfg = cfg['icons']
    state = {
        'schema': 2,
        'master_sha256': sha256(master),
        'source': str(icon_cfg.get('source', '.foxxdesk/assets/icon.png')),
        'generator': 'icon-assets-v4-config-safe-2026-09-04',
        'quality_profile': icon_cfg.get('quality_profile', 'best'),
        'padding_ratio': icon_cfg.get('padding_ratio', 0.0),
        'ios_background': icon_cfg.get('ios_background', '#FFFFFF'),
    }
    (root / STATE_REL).write_text(json.dumps(state, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def apply_icons(root: Path, cfg: dict[str, Any], *, apply: bool, force_regenerate: bool = False, ci_mode: bool = False) -> None:
    icons = cfg['icons']
    if not bool(icons.get('enabled', True)) or not bool(icons.get('apply_on_prepare', True)):
        print('[icons] desativado pela configuração')
        return
    master, seeded = resolve_master_icon(root, cfg, apply=apply)
    if not apply:
        print(f"[icons] dry-run: fonte={master.relative_to(root) if master.is_relative_to(root) else master}")
        return

    # res/icon.png remains a compatibility source for upstream scripts, but it is
    # always derived from the persistent master, never the other way around unless
    # the verified CI fallback had to seed a missing master.
    copy_if_changed(master, root / 'res/icon.png')

    # CI is byte-for-byte deterministic across Windows/macOS/Linux. Never install
    # Pillow into the runner Python and never regenerate PNG/ICO/ICNS per platform.
    # The committed overlay was generated locally from the master icon and is
    # authenticated by icon-state.json/master_sha256.
    if ci_mode:
        changed = restore_overlay_cache(root, master)
        print(f"[icons] CI determinístico: cache verificado restaurado: {changed} arquivo(s)")
        return

    if not pillow_available():
        changed = restore_overlay_cache(root, master)
        print(f"[icons] Pillow ausente; cache verificado restaurado: {changed} arquivo(s)")
        return

    from PIL import Image
    with Image.open(master) as im:
        width, height = im.size
    min_size = int(icons.get('min_source_size', 512))
    recommended = int(icons.get('recommended_source_size', 1024))
    if min(width, height) < min_size:
        raise RuntimeError(
            f"Ícone mestre {width}x{height} é menor que icons.min_source_size={min_size}; "
            "use uma fonte maior para evitar perda de qualidade."
        )
    if min(width, height) < recommended:
        print(f"[icons] AVISO: fonte {width}x{height}; recomendado >= {recommended}x{recommended} para melhor qualidade")

    cmd = [
        sys.executable, str(root / 'scripts/apply_foxxdesk_icon.py'),
        '--target', str(root),
        '--source', str(Path(icons.get('source', '.foxxdesk/assets/icon.png'))),
        '--ios-background', str(icons.get('ios_background', '#FFFFFF')),
        '--quality-profile', str(icons.get('quality_profile', 'best')),
        '--padding-ratio', str(icons.get('padding_ratio', 0.0)),
        '--png-compress-level', str(icons.get('png_compress_level', 9)),
        '--min-source-size', str(icons.get('min_source_size', 512)),
        '--recommended-source-size', str(icons.get('recommended_source_size', 1024)),
        '--apply', '--yes',
    ]
    if bool(icons.get('discover_by_name', True)):
        cmd.append('--discover-by-name')
    if bool(icons.get('create_brand_owned_assets', True)):
        cmd.append('--create-brand-owned-assets')
    if bool(icons.get('update_ios_contents', False)):
        cmd.append('--update-ios-contents')
    if not bool(icons.get('png_optimize', True)):
        cmd.append('--no-png-optimize')
    subprocess.run(cmd, cwd=str(root), check=True)
    refresh_overlay_and_state(root, cfg, master)
    suffix = ' (fonte recuperada)' if seeded else ''
    print(f"[icons] assets conferidos/regenerados a partir do ícone mestre{suffix}")


def run_rebrand(root: Path, cfg: dict[str, Any], profile: str, *, dry_run: bool) -> None:
    brand = cfg['brand']
    network = cfg['network']
    rebrand = cfg['rebrand']
    command = [
        sys.executable,
        str(root / 'scripts/apply_foxxdesk_rebrand.py'),
        '--target', str(root),
        '--profile', profile,
        '--skip-hbb-common-download',
        '--icons-managed-externally',
        '--preserve-hbb-common',
        '--display-name', str(brand['display_name']),
        '--slug', str(brand['slug']),
        '--company', str(brand.get('company') or 'FoxxDesk'),
        '--server', str(network['server']),
        '--relay', str(network.get('relay') or network['server']),
        '--key', str(network['key']),
        '--homepage', str(brand.get('homepage') or ''),
    ]
    if brand.get('maintainer_email'):
        command += ['--maintainer-email', str(brand['maintainer_email'])]
    if bool(rebrand.get('scan_all', False)):
        command.append('--scan-all')
    if bool(rebrand.get('remove_old_renamed', False)):
        command.append('--remove-old-renamed')
    command += ['--dry-run'] if dry_run else ['--apply', '--yes']
    subprocess.run(command, cwd=str(root), check=True)


def sync_dependency(root: Path, *, force: bool, write_pin: bool) -> None:
    command = [sys.executable, str(root / 'scripts/foxxdesk_sync_hbb_common.py'), '--target', str(root)]
    if force:
        command.append('--force')
    if write_pin:
        command.append('--write-pin')
    subprocess.run(command, cwd=str(root), check=True)


def ensure_ci_hooks(root: Path) -> None:
    subprocess.run(
        [sys.executable, str(root / 'scripts/foxxdesk_ci_hooks.py'), '--target', str(root), '--apply'],
        cwd=str(root), check=True,
    )


def check_ci_hooks(root: Path) -> None:
    subprocess.run(
        [sys.executable, str(root / 'scripts/foxxdesk_ci_hooks.py'), '--target', str(root), '--check'],
        cwd=str(root), check=True,
    )


def apply_runtime_defaults(root: Path) -> None:
    subprocess.run(
        [sys.executable, str(root / 'scripts/foxxdesk_runtime_defaults.py'), '--target', str(root), '--apply'],
        cwd=str(root), check=True,
    )


def apply_public_brand(root: Path) -> None:
    subprocess.run(
        [sys.executable, str(root / 'scripts/foxxdesk_public_brand.py'), '--target', str(root), '--apply'],
        cwd=str(root), check=True,
    )


def apply_build_compat(root: Path) -> None:
    subprocess.run(
        [sys.executable, str(root / 'scripts/foxxdesk_build_compat.py'), '--target', str(root), '--apply'],
        cwd=str(root), check=True,
    )


def validate(root: Path) -> None:
    subprocess.run(
        [sys.executable, str(root / 'scripts/foxxdesk_validate.py'), '--target', str(root)],
        cwd=str(root), check=True,
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Prepara atualização/build FoxxDesk de forma idempotente e upstream-safe')
    p.add_argument('--target', default='.')
    mode = p.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--dry-run', action='store_true')
    p.add_argument('--yes', action='store_true', help='Compatibilidade; processo é não interativo')
    p.add_argument('--ci', action='store_true', help='Modo CI somente leitura: valida a árvore commitada; não aplica rebrand nem sincroniza arquivos')
    p.add_argument('--bootstrap', action='store_true', help='Rebrand inicial/auditoria: usa bootstrap_profile (normalmente full)')
    p.add_argument('--sync-deps', action='store_true')
    p.add_argument('--force-sync-deps', action='store_true')
    p.add_argument('--profile', choices=['safe', 'runtime', 'full'], default=None)
    p.add_argument('--regenerate-icons', action='store_true', help='Mantido por compatibilidade; os ícones já são conferidos automaticamente')
    p.add_argument('--skip-icons', action='store_true')
    p.add_argument('--skip-validate', action='store_true')
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.target).expanduser().resolve()
    apply = not args.dry_run
    try:
        cfg, migrated = load_config(root, migrate_legacy=True, write_migration=apply)
        if migrated:
            print('[config] migração one-way do brand.json para foxxdesk.config.json: ' + ', '.join(migrated))
            print('[config] .foxxdesk/brand.json está obsoleto e não é mais lido como configuração principal')

        rebrand_cfg = cfg['rebrand']
        if args.profile:
            profile = args.profile
        elif args.bootstrap:
            profile = str(rebrand_cfg.get('bootstrap_profile', 'full'))
        elif args.ci:
            profile = str(rebrand_cfg.get('ci_profile', 'runtime'))
        else:
            profile = str(rebrand_cfg.get('profile', 'runtime'))

        # V6: CI is intentionally read-only. Build runners compile the exact tree
        # that was prepared locally and committed. This avoids injecting hooks into
        # every upstream checkout and survives workflow reorganizations much better.
        if args.ci:
            check_ci_hooks(root)
            subprocess.run(
                [sys.executable, str(root / 'scripts/foxxdesk_validate.py'), '--target', str(root), '--ci'],
                cwd=str(root), check=True,
            )
            print(f"FoxxDesk prepare OK ({SCRIPT_VERSION}, profile={profile}, modo=ci-read-only)")
            return 0

        if apply:
            # Local preparation removes legacy per-checkout hooks from upstream
            # workflows; it never injects new FoxxDesk steps into them.
            ensure_ci_hooks(root)

        should_sync = apply and (
            args.sync_deps or args.force_sync_deps or bool(cfg.get('upstream', {}).get('sync_hbb_common', True))
        )
        if should_sync:
            sync_dependency(root, force=args.force_sync_deps, write_pin=True)

        run_rebrand(root, cfg, profile, dry_run=not apply)

        if apply:
            # Public platform branding is owned by one semantic helper. This runs
            # after the legacy/runtime rebrand so Android/macOS/Windows can never
            # be left as RustDesk while the validator expects the configured name.
            apply_public_brand(root)
            apply_runtime_defaults(root)
            apply_build_compat(root)
            ensure_ci_hooks(root)
            if not args.skip_icons:
                apply_icons(
                    root, cfg, apply=True,
                    force_regenerate=args.regenerate_icons,
                    ci_mode=False,
                )

        if apply and not args.skip_validate:
            validate(root)
    except subprocess.CalledProcessError as exc:
        print(f'ERRO: etapa falhou com exit code {exc.returncode}', file=sys.stderr)
        return exc.returncode or 2
    except Exception as exc:
        print(f'ERRO: {exc}', file=sys.stderr)
        return 2

    print(f"FoxxDesk prepare OK ({SCRIPT_VERSION}, profile={profile}, modo={'apply' if apply else 'dry-run'})")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
