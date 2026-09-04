#!/usr/bin/env python3
"""Fast preflight checks for FoxxDesk branding and upstream compatibility."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_VERSION = "foxxdesk-validate-v1-2026-09-04"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def same_file(a: Path, b: Path) -> bool:
    if not a.is_file() or not b.is_file():
        return False
    return hashlib.sha256(a.read_bytes()).digest() == hashlib.sha256(b.read_bytes()).digest()


def check_contains(errors: list[str], path: Path, needle: str, label: str) -> None:
    if not path.is_file():
        errors.append(f"{label}: arquivo ausente ({path})")
    elif needle not in read(path):
        errors.append(f"{label}: não contém {needle!r}")


def dependency_compatibility(root: Path, cfg: dict) -> list[str]:
    # Import the sibling helper rather than duplicating evolving compatibility rules.
    sys.path.insert(0, str(root / "scripts"))
    try:
        import foxxdesk_sync_hbb_common as sync  # type: ignore
        errors = list(sync.compatibility_errors(root))
        try:
            expected, source = sync.expected_commit(root, cfg)
            current = sync.current_hbb_commit(root)
            if current is not None and current != expected:
                errors.append(f"revisão {current} != {expected} ({source})")
        except Exception as exc:
            errors.append(f"não foi possível determinar a revisão esperada: {exc}")
        return errors
    finally:
        try:
            sys.path.remove(str(root / "scripts"))
        except ValueError:
            pass


def main() -> int:
    p = argparse.ArgumentParser(description="Valida brand, ícone e compatibilidade do source FoxxDesk")
    p.add_argument("--target", default=".")
    args = p.parse_args()
    root = Path(args.target).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    cfg_path = root / ".foxxdesk/brand.json"
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        brand = cfg["brand"]
    except Exception as exc:
        print(f"ERRO: configuração inválida: {exc}", file=sys.stderr)
        return 2

    display = str(brand["display_name"])
    slug = str(brand["slug"])
    server = str(brand["server"])
    relay = str(brand.get("relay") or server)
    key = str(brand["key"])

    # Core branding invariants. Optional platform files are only checked when present.
    cargo = root / "Cargo.toml"
    if cargo.is_file():
        cargo_text = read(cargo)
        if not re.search(rf'(?m)^name\s*=\s*"{re.escape(slug)}"\s*$', cargo_text):
            errors.append(f"Cargo.toml: package principal não está como {slug}")
    else:
        errors.append("Cargo.toml ausente")

    hbb_cfg = root / "libs/hbb_common/src/config.rs"
    if hbb_cfg.is_file():
        t = read(hbb_cfg)
        for needle, label in [
            (f'RwLock::new("{display}".to_owned())', "APP_NAME"),
            (f'pub const DEFAULT_RENDEZVOUS_SERVER: &str = "{server}";', "servidor padrão"),
            (f'pub const DEFAULT_RELAY_SERVER: &str = "{relay}";', "relay padrão"),
            (f'pub const DEFAULT_CUSTOM_CLIENT_KEY: &str = "{key}";', "chave pública padrão"),
        ]:
            if needle not in t:
                errors.append(f"hbb_common config: {label} não aplicado")
    else:
        errors.append("libs/hbb_common/src/config.rs ausente")

    optional_invariants = [
        (root / "flutter/android/app/src/main/res/values/strings.xml", f">{display}<", "Android app_name"),
        (root / "flutter/android/app/src/main/AndroidManifest.xml", f'android:label="{display}"', "Android manifest"),
        (root / "flutter/macos/Runner/Configs/AppInfo.xcconfig", f"PRODUCT_NAME = {display}", "macOS product name"),
        (root / "flutter/windows/runner/Runner.rc", f'VALUE "ProductName", "{display}"', "Windows ProductName"),
    ]
    for path, needle, label in optional_invariants:
        if path.exists() and needle not in read(path):
            errors.append(f"{label}: brand não aplicado em {path.relative_to(root)}")

    master = root / ".foxxdesk/assets/icon.png"
    res_icon = root / "res/icon.png"
    if not master.is_file():
        errors.append("ícone mestre .foxxdesk/assets/icon.png ausente")
    elif not same_file(master, res_icon):
        errors.append("res/icon.png não corresponde ao ícone mestre persistente")

    manifest_path = root / ".foxxdesk/icon-overlay-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for rel in manifest.get("files", []):
            overlay = root / ".foxxdesk/icon-overlay" / rel
            target = root / rel
            if not overlay.is_file():
                errors.append(f"overlay de ícone ausente: {rel}")
            elif not target.is_file():
                errors.append(f"asset de ícone alvo ausente: {rel}")
            elif not same_file(overlay, target):
                errors.append(f"asset de ícone foi substituído pela atualização: {rel}")
    except Exception as exc:
        errors.append(f"manifesto de ícones inválido: {exc}")

    errors.extend(f"hbb_common: {e}" for e in dependency_compatibility(root, cfg))

    # Helpers must remain syntactically valid; catches accidental overwrite/merge corruption early.
    helpers = [
        "scripts/apply_foxxdesk_rebrand.py",
        "scripts/apply_foxxdesk_icon.py",
        "scripts/foxxdesk_sync_hbb_common.py",
        "scripts/foxxdesk_ci_hooks.py",
        "scripts/foxxdesk_prepare.py",
        "scripts/foxxdesk_validate.py",
    ]
    for rel in helpers:
        path = root / rel
        if not path.is_file():
            errors.append(f"helper ausente: {rel}")
            continue
        cp = subprocess.run([sys.executable, "-m", "py_compile", str(path)], cwd=str(root), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if cp.returncode != 0:
            errors.append(f"helper Python inválido {rel}: {cp.stderr.strip()}")

    hooks = subprocess.run(
        [sys.executable, str(root / "scripts/foxxdesk_ci_hooks.py"), "--target", str(root), "--check"],
        cwd=str(root), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if hooks.returncode != 0:
        errors.append("hooks de GitHub Actions ausentes: " + (hooks.stderr.strip() or hooks.stdout.strip()))

    if warnings:
        for item in warnings:
            print(f"AVISO: {item}")
    if errors:
        print("\nPRECHECK FALHOU:", file=sys.stderr)
        for item in errors:
            print(f" - {item}", file=sys.stderr)
        return 2

    print(f"FoxxDesk validation OK ({SCRIPT_VERSION})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
