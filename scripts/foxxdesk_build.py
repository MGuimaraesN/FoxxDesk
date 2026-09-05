#!/usr/bin/env python3
"""Conservative build.py wrapper driven by foxxdesk.config.json."""
from __future__ import annotations

import argparse
import platform
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from foxxdesk_config import load_config  # noqa: E402

SCRIPT_VERSION = 'foxxdesk-build-wrapper-v2-2026-09-04'


def build_command(root: Path, cfg: dict) -> list[str]:
    b = cfg.get('build', {})
    cmd = [sys.executable, str(root / 'build.py')]
    system = platform.system().lower()
    if b.get('flutter', True):
        cmd.append('--flutter')
    if b.get('hwcodec', False):
        cmd.append('--hwcodec')
    if b.get('unix_file_copy_paste', False) and system in {'linux', 'darwin'}:
        cmd.append('--unix-file-copy-paste')
    if b.get('vram', False) and system == 'windows':
        cmd.append('--vram')
    if b.get('portable', False) and system == 'windows':
        cmd.append('--portable')
    if b.get('skip_cargo', False):
        cmd.append('--skip-cargo')
    if b.get('skip_portable_pack', False) and system == 'windows':
        cmd.append('--skip-portable-pack')
    if b.get('screencapturekit', False) and system == 'darwin':
        cmd.append('--screencapturekit')
    if b.get('package'):
        cmd += ['--package', str(b['package'])]
    resource_features = b.get('resource_features') or []
    if resource_features:
        cmd += ['--feature', *[str(x) for x in resource_features]]
    return cmd


def main() -> int:
    p = argparse.ArgumentParser(description='Build FoxxDesk using the central JSON and only build.py-supported flags')
    p.add_argument('--target', default='.')
    p.add_argument('--prepare', action='store_true', help='Run foxxdesk_prepare.py before build')
    p.add_argument('--dry-run', action='store_true', help='Print the resolved command only')
    p.add_argument('extra', nargs=argparse.REMAINDER, help='Extra build.py arguments after --')
    args = p.parse_args()
    root = Path(args.target).expanduser().resolve()
    try:
        cfg, _ = load_config(root, migrate_legacy=True, write_migration=False)
        if args.prepare:
            prep = [sys.executable, str(root / 'scripts/foxxdesk_prepare.py'), '--target', str(root), '--apply', '--yes', '--sync-deps']
            if args.dry_run:
                print('PREPARE:', shlex.join(prep))
            else:
                subprocess.run(prep, cwd=str(root), check=True)
        cmd = build_command(root, cfg)
        if args.extra:
            extra = args.extra[1:] if args.extra and args.extra[0] == '--' else args.extra
            cmd += extra
        print('BUILD:', shlex.join(cmd))
        if not args.dry_run:
            subprocess.run(cmd, cwd=str(root), check=True)
    except subprocess.CalledProcessError as exc:
        return exc.returncode or 2
    except Exception as exc:
        print(f'ERRO: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
