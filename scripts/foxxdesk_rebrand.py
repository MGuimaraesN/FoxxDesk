#!/usr/bin/env python3
"""FoxxDesk V11 rebrand orchestrator.

One command owns the safe rebrand flow:
1. load .foxxdesk/foxxdesk.config.json
2. resolve/sync the exact hbb_common commit for the detected RustDesk version
3. apply patch-only rebrand while preserving hbb_common
4. apply semantic public branding
5. apply runtime server/relay/key defaults in the parent crate
6. apply/check narrow build compatibility patches
7. re-check hbb_common exact compatibility

It never tracks hbb_common/main.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from foxxdesk_config import load_config  # noqa: E402

SCRIPT_VERSION = "foxxdesk-rebrand-v11-exact-hbb-2026-09-06"


def run(cmd: list[str], root: Path) -> None:
    subprocess.run(cmd, cwd=str(root), check=True)


def sync_hbb(root: Path, cfg: dict, *, check_only: bool, force_override: bool | None) -> None:
    upstream = cfg.get("upstream", {})
    if not bool(upstream.get("sync_hbb_common", True)):
        print("[hbb] sincronização desativada no config")
        return

    cmd = [sys.executable, str(root / "scripts/foxxdesk_sync_hbb_common.py"), "--target", str(root)]
    if check_only:
        cmd.append("--check")
    else:
        if bool(upstream.get("persist_resolved_pin", True)):
            cmd.append("--write-pin")
        force = bool(upstream.get("force_refresh_each_prepare", True)) if force_override is None else force_override
        if force:
            cmd.append("--force")
    run(cmd, root)


def rebrand_command(root: Path, cfg: dict, profile: str, *, dry_run: bool) -> list[str]:
    brand = cfg["brand"]
    network = cfg["network"]
    rebrand = cfg["rebrand"]
    cmd = [
        sys.executable,
        str(root / "scripts/apply_foxxdesk_rebrand.py"),
        "--target", str(root),
        "--profile", profile,
        "--skip-hbb-common-download",
        "--preserve-hbb-common",
        "--icons-managed-externally",
        "--display-name", str(brand["display_name"]),
        "--slug", str(brand["slug"]),
        "--company", str(brand.get("company") or brand["display_name"]),
        "--server", str(network["server"]),
        "--relay", str(network.get("relay") or network["server"]),
        "--key", str(network["key"]),
        "--homepage", str(brand.get("homepage") or ""),
    ]
    if brand.get("maintainer_email"):
        cmd += ["--maintainer-email", str(brand["maintainer_email"])]
    if bool(rebrand.get("scan_all", False)):
        cmd.append("--scan-all")
    if bool(rebrand.get("remove_old_renamed", False)):
        cmd.append("--remove-old-renamed")
    cmd += ["--dry-run"] if dry_run else ["--apply", "--yes"]
    return cmd


def helper(root: Path, name: str, mode: str) -> None:
    run([sys.executable, str(root / "scripts" / name), "--target", str(root), mode], root)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Aplica o rebrand FoxxDesk V11 com hbb_common exato da versão")
    p.add_argument("--target", default=".")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Aplica as alterações (padrão se nenhum modo for informado)")
    mode.add_argument("--dry-run", action="store_true", help="Valida/simula sem alterar")
    p.add_argument("--yes", action="store_true", help="Compatibilidade; o fluxo é não interativo")
    p.add_argument("--profile", choices=["safe", "runtime", "full"], default=None)
    p.add_argument("--force-hbb-refresh", action="store_true", help="Força fetch/checkout do commit exato do hbb_common nesta execução")
    p.add_argument("--no-force-hbb-refresh", action="store_true", help="Só baixa hbb_common se estiver ausente/incorreto nesta execução")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.target).expanduser().resolve()
    dry_run = bool(args.dry_run)
    try:
        cfg, migrated = load_config(root, migrate_legacy=True, write_migration=not dry_run)
        if migrated:
            print("[config] migração aplicada: " + ", ".join(migrated))
        profile = args.profile or str(cfg.get("rebrand", {}).get("profile", "runtime"))

        if args.force_hbb_refresh and args.no_force_hbb_refresh:
            raise RuntimeError("use apenas uma das opções --force-hbb-refresh/--no-force-hbb-refresh")
        force_override = True if args.force_hbb_refresh else (False if args.no_force_hbb_refresh else None)

        # Always resolve/check the exact hbb_common before touching source branding.
        sync_hbb(root, cfg, check_only=dry_run, force_override=force_override)

        if dry_run:
            cp = subprocess.run(rebrand_command(root, cfg, profile, dry_run=True), cwd=str(root))
            # Legacy dry-run returns 1 when there are planned changes/pending items.
            # Treat 0/1 as a successful simulation; >=2 remains a real execution error.
            if cp.returncode not in (0, 1):
                raise subprocess.CalledProcessError(cp.returncode, rebrand_command(root, cfg, profile, dry_run=True))
            print("[dry-run] rebrand analisado; alterações planejadas não foram gravadas")
        else:
            run(rebrand_command(root, cfg, profile, dry_run=False), root)
            helper(root, "foxxdesk_public_brand.py", "--apply")
            helper(root, "foxxdesk_runtime_defaults.py", "--apply")
            helper(root, "foxxdesk_build_compat.py", "--apply")
            helper(root, "foxxdesk_public_brand.py", "--check")
            helper(root, "foxxdesk_runtime_defaults.py", "--check")
            helper(root, "foxxdesk_build_compat.py", "--check")
            # Final dependency check ensures no rebrand helper touched the submodule.
            sync_hbb(root, cfg, check_only=True, force_override=False)

        print(f"FoxxDesk rebrand OK ({SCRIPT_VERSION}, profile={profile}, modo={'dry-run' if dry_run else 'apply'})")
        return 0
    except subprocess.CalledProcessError as exc:
        print(f"ERRO: etapa falhou com exit code {exc.returncode}", file=sys.stderr)
        return exc.returncode or 2
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
