#!/usr/bin/env python3
"""Prepare a RustDesk/FoxxDesk checkout for a deterministic FoxxDesk build.

This is the stable entrypoint to run after copying a new upstream update and in
GitHub Actions. Brand configuration and the master icon live under .foxxdesk,
which is intentionally outside the upstream files normally replaced on update.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_VERSION = "foxxdesk-prepare-v1-2026-09-04"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def copy_if_changed(src: Path, dst: Path) -> bool:
    if not src.is_file():
        raise FileNotFoundError(f"Fonte ausente: {src}")
    if dst.is_file() and src.read_bytes() == dst.read_bytes():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def restore_icons(root: Path) -> int:
    """Restore pre-generated icon assets without requiring Pillow in CI."""
    changed = 0
    master = root / ".foxxdesk/assets/icon.png"
    if copy_if_changed(master, root / "res/icon.png"):
        changed += 1

    manifest_path = root / ".foxxdesk/icon-overlay-manifest.json"
    manifest = load_json(manifest_path)
    for rel in manifest.get("files", []):
        rel_path = Path(rel)
        src = root / ".foxxdesk/icon-overlay" / rel_path
        dst = root / rel_path
        if not src.is_file():
            raise FileNotFoundError(f"Asset de overlay ausente: {src}")
        if copy_if_changed(src, dst):
            changed += 1
    return changed


def regenerate_icon_overlay(root: Path, ios_background: str) -> None:
    """Regenerate platform assets and refresh the persistent icon overlay."""
    generator = root / "scripts/apply_foxxdesk_icon.py"
    cmd = [
        sys.executable,
        str(generator),
        "--target", str(root),
        "--source", "res/icon.png",
        "--ios-background", ios_background,
        "--apply", "--yes",
    ]
    subprocess.run(cmd, cwd=str(root), check=True)

    # Rebuild the overlay manifest from the generator itself so future icon targets
    # are picked up automatically when the helper evolves.
    import importlib.util
    spec = importlib.util.spec_from_file_location("foxxdesk_icon_generator", generator)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    paths = [x["path"] for x in module.ALL_IMAGE_ASSETS]
    paths += [x["path"] for x in module.SVG_ASSETS]
    paths += [x["path"] for x in module.ICO_ASSETS]
    paths += [x["path"] for x in module.ICNS_ASSETS]
    paths += ["res/icon.png"]
    files = []
    for rel in sorted(set(paths)):
        src = root / rel
        if not src.is_file():
            continue
        dst = root / ".foxxdesk/icon-overlay" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        files.append(rel)
    (root / ".foxxdesk/icon-overlay-manifest.json").write_text(
        json.dumps({"schema": 1, "files": files}, indent=2) + "\n", encoding="utf-8"
    )


def run_rebrand(root: Path, cfg: dict, profile: str, *, dry_run: bool) -> None:
    brand = cfg["brand"]
    command = [
        sys.executable,
        str(root / "scripts/apply_foxxdesk_rebrand.py"),
        "--target", str(root),
        "--profile", profile,
        "--skip-hbb-common-download",
        "--server", str(brand["server"]),
        "--relay", str(brand.get("relay") or brand["server"]),
        "--key", str(brand["key"]),
    ]
    if dry_run:
        command += ["--dry-run"]
    else:
        command += ["--apply", "--yes"]
    subprocess.run(command, cwd=str(root), check=True)


def sync_dependency(root: Path, *, force: bool, write_pin: bool) -> None:
    command = [sys.executable, str(root / "scripts/foxxdesk_sync_hbb_common.py"), "--target", str(root)]
    if force:
        command.append("--force")
    if write_pin:
        command.append("--write-pin")
    subprocess.run(command, cwd=str(root), check=True)


def ensure_ci_hooks(root: Path) -> None:
    subprocess.run(
        [sys.executable, str(root / "scripts/foxxdesk_ci_hooks.py"), "--target", str(root), "--apply"],
        cwd=str(root), check=True,
    )


def validate(root: Path) -> None:
    subprocess.run([sys.executable, str(root / "scripts/foxxdesk_validate.py"), "--target", str(root)], cwd=str(root), check=True)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Prepara uma atualização para build FoxxDesk sem perder brand/ícones")
    p.add_argument("--target", default=".")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Aplica a preparação (padrão fora de --dry-run)")
    mode.add_argument("--dry-run", action="store_true", help="Executa o rebrand em dry-run e não sincroniza dependências")
    p.add_argument("--yes", action="store_true", help="Mantido por compatibilidade; a preparação é não interativa")
    p.add_argument("--ci", action="store_true", help="Modo CI: profile safe + sincronização exata e validação estrita")
    p.add_argument("--sync-deps", action="store_true", help="Sincroniza hbb_common com a revisão compatível")
    p.add_argument("--force-sync-deps", action="store_true", help="Força restaurar exatamente o commit compatível")
    p.add_argument("--profile", choices=["safe", "full"], default=None, help="Sobrescreve o profile definido pela política")
    p.add_argument("--regenerate-icons", action="store_true", help="Regenera todos os tamanhos via Pillow e atualiza o overlay persistente")
    p.add_argument("--skip-validate", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.target).expanduser().resolve()
    cfg_path = root / ".foxxdesk/brand.json"
    try:
        cfg = load_json(cfg_path)
    except Exception as exc:
        print(f"ERRO: não foi possível ler {cfg_path}: {exc}", file=sys.stderr)
        return 2

    policy = cfg.get("policy", {})
    profile = args.profile or (policy.get("ci_profile", "safe") if args.ci else policy.get("local_update_profile", "full"))
    apply = not args.dry_run

    try:
        if apply:
            ensure_ci_hooks(root)
            icon_changes = restore_icons(root)
            print(f"[prepare] overlay de ícones restaurado: {icon_changes} arquivo(s) alterado(s)")
        else:
            icon_changes = 0

        should_sync = apply and (args.sync_deps or args.force_sync_deps or args.ci or bool(policy.get("sync_dependency_in_ci") and args.ci))
        if should_sync:
            sync_dependency(root, force=(args.force_sync_deps or args.ci), write_pin=not args.ci)

        # Dependency sync restores a clean hbb_common, so brand is always applied after it.
        run_rebrand(root, cfg, profile, dry_run=not apply)

        if apply and args.regenerate_icons:
            # Ensure master source is copied before calling the legacy generator.
            copy_if_changed(root / ".foxxdesk/assets/icon.png", root / "res/icon.png")
            regenerate_icon_overlay(root, str(cfg["brand"].get("ios_background", "#FFFFFF")))
            print("[prepare] assets de ícone regenerados e overlay atualizado")

        # Re-assert CI hooks and icon overlay after the legacy patcher; both must remain
        # persistent even when upstream workflow files were replaced.
        if apply:
            ensure_ci_hooks(root)
            restore_icons(root)

        if not args.skip_validate and apply:
            validate(root)
    except subprocess.CalledProcessError as exc:
        print(f"ERRO: etapa falhou com exit code {exc.returncode}", file=sys.stderr)
        return exc.returncode or 2
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2

    print(f"FoxxDesk prepare OK ({SCRIPT_VERSION}, profile={profile}, modo={'apply' if apply else 'dry-run'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
