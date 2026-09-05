#!/usr/bin/env python3
"""Remove/check legacy FoxxDesk prepare hooks from upstream workflows.

V5 architecture deliberately does NOT inject prepare hooks into RustDesk workflows.
The repository must be prepared locally and committed. GitHub Actions validates the
committed tree in a single preflight job, then the upstream reusable workflow builds
that exact committed source.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_VERSION = "foxxdesk-ci-hooks-v5-no-upstream-injection-2026-09-05"
HOOK_USES = "uses: ./.github/actions/prepare-foxxdesk"
OWN_WORKFLOW = ".github/workflows/foxxdesk-build.yml"


def leading_spaces(s: str) -> int:
    return len(s) - len(s.lstrip(" "))


def step_bounds(lines: list[str], uses_idx: int) -> tuple[int, int]:
    uses_indent = leading_spaces(lines[uses_idx])
    step_indent = max(0, uses_indent - 2)
    start = uses_idx
    while start >= 0:
        line = lines[start]
        if leading_spaces(line) == step_indent and line.lstrip().startswith("- "):
            break
        start -= 1
    if start < 0:
        raise ValueError(f"não foi possível localizar início do step na linha {uses_idx + 1}")
    end = uses_idx + 1
    while end < len(lines):
        line = lines[end]
        if leading_spaces(line) == step_indent and line.lstrip().startswith("- "):
            break
        end += 1
    return start, end


def remove_legacy_hooks(path: Path) -> int:
    if not path.is_file():
        return 0
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    indexes = [
        i for i, line in enumerate(lines)
        if HOOK_USES in line and not line.lstrip().startswith("#")
    ]
    changed = 0
    for idx in reversed(indexes):
        try:
            start, end = step_bounds(lines, idx)
        except ValueError:
            continue
        if start > 0 and not lines[start - 1].strip():
            start -= 1
        del lines[start:end]
        changed += 1
    if changed:
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return changed


def upstream_hook_files(root: Path) -> list[str]:
    workflows = root / ".github/workflows"
    if not workflows.is_dir():
        return []
    found: list[str] = []
    for path in sorted(list(workflows.glob("*.yml")) + list(workflows.glob("*.yaml"))):
        rel = path.relative_to(root).as_posix()
        if rel == OWN_WORKFLOW:
            continue
        if HOOK_USES in path.read_text(encoding="utf-8", errors="ignore"):
            found.append(rel)
    return found


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Remove ou valida hooks FoxxDesk legados em workflows upstream")
    p.add_argument("--target", default=".")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.target).expanduser().resolve()
    workflows = root / ".github/workflows"

    if args.apply:
        removed = 0
        if workflows.is_dir():
            for path in sorted(list(workflows.glob("*.yml")) + list(workflows.glob("*.yaml"))):
                rel = path.relative_to(root).as_posix()
                if rel == OWN_WORKFLOW:
                    continue
                removed += remove_legacy_hooks(path)
        print(f"FoxxDesk CI workflow cleanup OK: {removed} hook(s) legado(s) removido(s) ({SCRIPT_VERSION})")
        return 0

    legacy = upstream_hook_files(root)
    if legacy:
        print(
            "Hooks FoxxDesk legados ainda existem em workflows upstream. "
            "Rode `python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps` e faça commit:",
            file=sys.stderr,
        )
        for rel in legacy:
            print(f" - {rel}", file=sys.stderr)
        return 2

    print(f"FoxxDesk CI workflow layout OK ({SCRIPT_VERSION})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
