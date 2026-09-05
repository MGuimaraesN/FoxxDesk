#!/usr/bin/env python3
"""Synchronize libs/hbb_common to the revision compatible with the RustDesk tree.

The old FoxxDesk rebrand downloaded hbb_common/main.zip. That is unsafe because
RustDesk and hbb_common evolve together. This helper resolves/preserves the
submodule commit (preferred) or a version pin and never tracks hbb_common/main.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SCRIPT_VERSION = "foxxdesk-hbb-sync-v2-atomic-same-volume-2026-09-05"
HBB_URL = "https://github.com/rustdesk/hbb_common.git"
CONFIG_REL = Path(".foxxdesk/foxxdesk.config.json")
HBB_REL = Path("libs/hbb_common")
MARKER = ".foxxdesk_upstream_commit"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from foxxdesk_config import load_config, save_config  # noqa: E402


class SyncError(RuntimeError):
    pass


def run(cmd: list[str], *, cwd: Path, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SyncError(f"Configuração ausente: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SyncError(f"JSON inválido em {path}: {exc}") from exc


def cargo_version(root: Path) -> str:
    text = (root / "Cargo.toml").read_text(encoding="utf-8", errors="ignore")
    # Only the first package version before any dependency table.
    m = re.search(r"(?ms)^\[package\].*?^version\s*=\s*\"([^\"]+)\"", text)
    if not m:
        raise SyncError("Não foi possível detectar a versão no Cargo.toml")
    return m.group(1).strip()


def gitlink_commit(root: Path) -> str | None:
    """Return the gitlink SHA when libs/hbb_common is a real submodule."""
    try:
        cp = run(["git", "ls-files", "--stage", "libs/hbb_common"], cwd=root, capture=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    for line in cp.stdout.splitlines():
        # 160000 <sha> 0\tlibs/hbb_common
        m = re.match(r"160000\s+([0-9a-fA-F]{40})\s+\d+\s+libs/hbb_common$", line.strip())
        if m:
            return m.group(1).lower()
    return None


def current_hbb_commit(root: Path) -> str | None:
    hbb = root / HBB_REL
    marker = hbb / MARKER
    if marker.is_file():
        value = marker.read_text(encoding="utf-8", errors="ignore").strip().lower()
        if re.fullmatch(r"[0-9a-f]{40}", value):
            return value
    if not hbb.exists():
        return None
    try:
        cp = run(["git", "rev-parse", "HEAD"], cwd=hbb, capture=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    value = cp.stdout.strip().lower()
    return value if re.fullmatch(r"[0-9a-f]{40}", value) else None


def source_requirements(root: Path) -> list[str]:
    required: list[str] = []
    root_files = [
        root / "src/client.rs",
        root / "src/platform/linux.rs",
        root / "src/flutter_ffi.rs",
        root / "src/server/audio_service.rs",
    ]
    joined = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in root_files if p.is_file())
    if "LINK_HEADLESS_LINUX_SUPPORT" in joined:
        required.append("LINK_HEADLESS_LINUX_SUPPORT")
    if "OPTION_ALLOW_LINUX_HEADLESS" in joined:
        required.append("OPTION_ALLOW_LINUX_HEADLESS")
    if "aligned_u8_vec" in joined and re.search(r"align_to_32\s*\([^)]*Vec<u8>[^)]*\)\s*->\s*Vec<u8>", joined):
        required.append("aligned_u8_vec_returns_vec")
    return required


def compatibility_errors(root: Path) -> list[str]:
    hbb = root / HBB_REL
    errors: list[str] = []
    cargo = hbb / "Cargo.toml"
    config = hbb / "src/config.rs"
    mem = hbb / "src/mem.rs"
    if not cargo.is_file():
        return ["libs/hbb_common/Cargo.toml ausente"]
    config_text = config.read_text(encoding="utf-8", errors="ignore") if config.is_file() else ""
    mem_text = mem.read_text(encoding="utf-8", errors="ignore") if mem.is_file() else ""
    req = source_requirements(root)
    if "LINK_HEADLESS_LINUX_SUPPORT" in req and "pub const LINK_HEADLESS_LINUX_SUPPORT" not in config_text:
        errors.append("o source usa LINK_HEADLESS_LINUX_SUPPORT, mas hbb_common não o define")
    if "OPTION_ALLOW_LINUX_HEADLESS" in req and "OPTION_ALLOW_LINUX_HEADLESS" not in config_text:
        errors.append("o source usa OPTION_ALLOW_LINUX_HEADLESS, mas hbb_common não o define")
    if "aligned_u8_vec_returns_vec" in req:
        # RustDesk 1.4.9 expects the old API returning Vec<u8>.
        if not re.search(r"fn\s+aligned_u8_vec\s*\([^)]*\)\s*->\s*Vec\s*<\s*u8\s*>", mem_text, flags=re.S):
            errors.append("audio_service espera aligned_u8_vec -> Vec<u8>, mas hbb_common expõe outra API")
    return errors


def github_submodule_commit(ref: str) -> str:
    encoded = urllib.parse.quote(ref, safe="")
    url = f"https://api.github.com/repos/rustdesk/rustdesk/contents/libs/hbb_common?ref={encoded}"
    req = urllib.request.Request(url, headers={"User-Agent": "FoxxDesk-CI/1.0", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            data = json.load(response)
    except Exception as exc:  # network/API errors become an actionable message
        raise SyncError(f"Falha ao resolver hbb_common do RustDesk ref '{ref}' via GitHub: {exc}") from exc
    sha = str(data.get("sha", "")).lower()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise SyncError(f"GitHub não retornou um SHA de submódulo válido para RustDesk ref '{ref}'")
    return sha


def expected_commit(root: Path, cfg: dict) -> tuple[str, str]:
    # 1) Explicit override wins. Useful for unreleased/master snapshots.
    env_commit = os.environ.get("FOXXDESK_HBB_COMMON_COMMIT", "").strip().lower()
    if env_commit:
        if not re.fullmatch(r"[0-9a-f]{40}", env_commit):
            raise SyncError("FOXXDESK_HBB_COMMON_COMMIT deve ser um SHA completo de 40 caracteres")
        return env_commit, "FOXXDESK_HBB_COMMON_COMMIT"

    version = cargo_version(root)
    upstream = cfg.get("upstream", {})

    # 2) A committed version pin is deterministic and must beat a possibly stale
    # gitlink left behind when a release ZIP was copied over an existing checkout.
    pins = upstream.get("hbb_common_pins", {}) or {}
    pin = str(pins.get(version, "")).strip().lower()
    if pin:
        if not re.fullmatch(r"[0-9a-f]{40}", pin):
            raise SyncError(f"Pin hbb_common inválido para {version} em {CONFIG_REL}")
        return pin, f"pin da versão {version}"

    # 3) For a new release, resolve the hbb_common gitlink from that SAME RustDesk
    # ref. This avoids ever following hbb_common/main independently.
    configured_ref = str(upstream.get("rustdesk_ref", "auto")).strip()
    refs = [configured_ref] if configured_ref not in {"", "auto"} else [version, f"v{version}"]
    api_errors: list[str] = []
    for ref in dict.fromkeys(refs):
        try:
            return github_submodule_commit(ref), f"submódulo do RustDesk ref {ref}"
        except SyncError as api_error:
            api_errors.append(str(api_error))

    # 4) Offline/local fallback only. Compatibility validation still runs, so
    # a stale pointer is rejected rather than silently compiled.
    gitlink = gitlink_commit(root)
    if gitlink:
        reason = " | ".join(api_errors)
        return gitlink, f"gitlink do repositório (fallback; GitHub indisponível/ref não resolvido: {reason})"
    raise SyncError("Não foi possível resolver o hbb_common compatível. " + " | ".join(api_errors))


def sync_real_submodule(root: Path, expected: str) -> None:
    run(["git", "submodule", "sync", "--recursive"], cwd=root)
    # Initialize the submodule first, then explicitly place it at the resolved
    # compatible SHA. This also repairs a stale gitlink after copying an upstream
    # release over an older working tree.
    run(["git", "-c", "core.longpaths=true", "submodule", "update", "--init", "--force", "--recursive", "--depth", "1", "libs/hbb_common"], cwd=root)
    hbb = root / HBB_REL
    try:
        run(["git", "fetch", "--depth", "1", "origin", expected], cwd=hbb)
        checkout_ref = "FETCH_HEAD"
    except subprocess.CalledProcessError:
        run(["git", "fetch", "--prune", "origin"], cwd=hbb)
        checkout_ref = expected
    run(["git", "checkout", "--detach", "--force", checkout_ref], cwd=hbb)
    got = current_hbb_commit(root)
    if got != expected:
        raise SyncError(f"Submódulo hbb_common ficou em {got or 'desconhecido'}, esperado {expected}")


def _rmtree_onerror(func, path, exc_info) -> None:
    """Make read-only Git files writable and retry removal (Windows-safe)."""
    try:
        os.chmod(path, 0o700)
        func(path)
    except Exception:
        pass


def robust_rmtree(path: Path) -> None:
    if not path.exists():
        return
    shutil.rmtree(path, onerror=_rmtree_onerror)


def clone_exact_revision(root: Path, expected: str) -> None:
    """Install an exact vendored hbb_common revision with an atomic same-volume swap.

    The staging directory deliberately lives beside libs/hbb_common. GitHub's Windows
    runners keep TEMP on C: while the workspace is on D:. Staging in system TEMP and
    moving into the workspace triggers WinError 17 (cross-volume rename) and can leave
    a half-restored backup. A sibling staging directory avoids that class of failure.
    """
    destination = root / HBB_REL
    parent = destination.parent
    parent.mkdir(parents=True, exist_ok=True)

    staging = parent / ".hbb_common.foxxdesk-new"
    backup = parent / ".hbb_common.foxxdesk-old"
    robust_rmtree(staging)
    robust_rmtree(backup)

    try:
        run(["git", "-c", "core.longpaths=true", "init", str(staging)], cwd=root)
        run(["git", "-C", str(staging), "remote", "add", "origin", HBB_URL], cwd=root)
        try:
            run(["git", "-C", str(staging), "fetch", "--depth", "1", "origin", expected], cwd=root)
            checkout_ref = "FETCH_HEAD"
        except subprocess.CalledProcessError:
            run(["git", "-C", str(staging), "fetch", "--prune", "origin"], cwd=root)
            checkout_ref = expected
        run(["git", "-C", str(staging), "checkout", "--detach", "--force", checkout_ref], cwd=root)
        got = run(["git", "-C", str(staging), "rev-parse", "HEAD"], cwd=root, capture=True).stdout.strip().lower()
        if got != expected:
            raise SyncError(f"Clone retornou {got}, esperado {expected}")

        # Convert the checkout into a vendored tree before the swap. Removing .git here
        # also avoids Windows file-lock/read-only issues during later cleanup.
        robust_rmtree(staging / ".git")
        (staging / MARKER).write_text(expected + "\n", encoding="utf-8")

        if destination.exists():
            destination.rename(backup)
        try:
            staging.rename(destination)  # same parent => same filesystem/drive, atomic
        except Exception:
            robust_rmtree(destination)
            if backup.exists() and not destination.exists():
                backup.rename(destination)
            raise
        robust_rmtree(backup)
    except Exception:
        robust_rmtree(staging)
        # If a previous attempt left a backup and destination vanished, restore it.
        if backup.exists() and not destination.exists():
            backup.rename(destination)
        raise


def persist_version_pin(root: Path, cfg: dict, commit: str) -> bool:
    """Persist a resolved pin so later CI jobs do not depend on API resolution."""
    version = cargo_version(root)
    upstream = cfg.setdefault("upstream", {})
    pins = upstream.setdefault("hbb_common_pins", {})
    if str(pins.get(version, "")).lower() == commit.lower():
        return False
    pins[version] = commit.lower()
    save_config(root, cfg)
    return True


def synchronize(root: Path, *, force: bool = False, check_only: bool = False) -> tuple[bool, str]:
    cfg, _ = load_config(root, migrate_legacy=True, write_migration=False)
    expected, source = expected_commit(root, cfg)
    current = current_hbb_commit(root)
    compat_before = compatibility_errors(root)

    if check_only:
        if current and current != expected:
            raise SyncError(f"hbb_common em {current}, esperado {expected} ({source})")
        if compat_before:
            raise SyncError("; ".join(compat_before))
        return False, expected

    if not force and not compat_before and (current in {None, expected}):
        # A copied upstream tree may not have .git/marker; if its API matches the source,
        # do not require network just to prove provenance during a local preparation.
        return False, expected

    print(f"[hbb] sincronizando revisão {expected} ({source})")
    if gitlink_commit(root):
        sync_real_submodule(root, expected)
    else:
        clone_exact_revision(root, expected)

    errors = compatibility_errors(root)
    if errors:
        raise SyncError("hbb_common sincronizado, mas ainda incompatível: " + "; ".join(errors))
    return True, expected


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sincroniza hbb_common com a revisão compatível do RustDesk/FoxxDesk")
    p.add_argument("--target", default=".", help="Raiz do projeto")
    p.add_argument("--force", action="store_true", help="Força restaurar exatamente o commit esperado")
    p.add_argument("--check", action="store_true", help="Somente valida; não baixa nem altera")
    p.add_argument("--write-pin", action="store_true", help="Grava o SHA resolvido em .foxxdesk/foxxdesk.config.json para builds reprodutíveis")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.target).expanduser().resolve()
    try:
        changed, expected = synchronize(root, force=args.force, check_only=args.check)
        if args.write_pin and not args.check:
            cfg, _ = load_config(root, migrate_legacy=True, write_migration=False)
            if persist_version_pin(root, cfg, expected):
                print(f"[hbb] pin persistido para RustDesk {cargo_version(root)}")
    except (SyncError, FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"ERRO hbb_common: {exc}", file=sys.stderr)
        return 2
    print(f"hbb_common OK: {expected}" + (" (sincronizado)" if changed else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
