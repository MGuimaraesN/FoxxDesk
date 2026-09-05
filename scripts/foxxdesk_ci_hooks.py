#!/usr/bin/env python3
"""Install/check persistent FoxxDesk prepare hooks in upstream build workflows.

Upstream updates can overwrite flutter-build.yml/bridge.yml/ci.yml. This script
re-injects the local composite action after every active actions/checkout step,
so each isolated GitHub Actions job prepares the same source/dependency tuple.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_VERSION = "foxxdesk-ci-hooks-v3-committed-manual-path-2026-09-05"
HOOK_USES = "uses: ./.github/actions/prepare-foxxdesk"
TARGETS = [
    # Only workflows used by the manual FoxxDesk build need the prepare hook.
    # Do not inject FoxxDesk preparation into upstream CI/push/PR workflows.
    ".github/workflows/flutter-build.yml",
    ".github/workflows/bridge.yml",
]
FOXDESK_OWNED_WORKFLOW = ".github/workflows/foxxdesk-build.yml"


def leading_spaces(s: str) -> int:
    return len(s) - len(s.lstrip(" "))


def active_checkout_indexes(lines: list[str]) -> list[int]:
    return [
        i for i, line in enumerate(lines)
        if not line.lstrip().startswith("#") and "uses: actions/checkout@" in line
    ]


def step_bounds(lines: list[str], checkout_use_idx: int) -> tuple[int, int, int]:
    """Return (step_start, next_step, step_indent)."""
    uses_indent = leading_spaces(lines[checkout_use_idx])
    step_indent = max(0, uses_indent - 2)
    start = checkout_use_idx
    while start >= 0:
        line = lines[start]
        if leading_spaces(line) == step_indent and line.lstrip().startswith("- "):
            break
        start -= 1
    if start < 0:
        raise ValueError(f"não foi possível localizar início do step na linha {checkout_use_idx + 1}")
    end = checkout_use_idx + 1
    while end < len(lines):
        line = lines[end]
        if leading_spaces(line) == step_indent and line.lstrip().startswith("- "):
            break
        end += 1
    return start, end, step_indent


def step_end_from_start(lines: list[str], start: int, step_indent: int) -> int:
    end = start + 1
    while end < len(lines):
        if leading_spaces(lines[end]) == step_indent and lines[end].lstrip().startswith("- "):
            break
        end += 1
    return end


def missing_hooks(path: Path) -> list[int]:
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    missing: list[int] = []
    for idx in active_checkout_indexes(lines):
        _, end, _ = step_bounds(lines, idx)
        # Hook must be the immediately following step (blank/comment lines allowed).
        j = end
        while j < len(lines) and (not lines[j].strip() or lines[j].lstrip().startswith("#")):
            j += 1
        if j >= len(lines):
            missing.append(idx + 1)
            continue
        hook_next = step_end_from_start(lines, j, leading_spaces(lines[j]))
        block = "\n".join(lines[j:hook_next])
        if HOOK_USES not in block:
            missing.append(idx + 1)
    return missing


def install_hooks(path: Path) -> int:
    if not path.is_file():
        return 0
    lines = path.read_text(encoding="utf-8").splitlines()
    changed = 0
    # Work backwards so inserted lines do not invalidate earlier indexes.
    for idx in reversed(active_checkout_indexes(lines)):
        _, end, step_indent = step_bounds(lines, idx)
        j = end
        while j < len(lines) and (not lines[j].strip() or lines[j].lstrip().startswith("#")):
            j += 1
        already = False
        if j < len(lines) and leading_spaces(lines[j]) == step_indent and lines[j].lstrip().startswith("- "):
            hook_next = step_end_from_start(lines, j, step_indent)
            already = HOOK_USES in "\n".join(lines[j:hook_next])
        if already:
            continue
        indent = " " * step_indent
        block = [
            "",
            f"{indent}- name: Prepare FoxxDesk source",
            f"{indent}  {HOOK_USES}",
        ]
        lines[end:end] = block
        changed += 1
    if changed:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changed


def remove_hook_steps(path: Path) -> int:
    """Remove FoxxDesk prepare steps from workflows that are not part of manual build.

    Older FoxxDesk packages injected the hook into ci.yml, causing normal push/PR CI
    to run the rebrand/dependency preparation. We only keep hooks in bridge.yml and
    flutter-build.yml, which are reached by the manual FoxxDesk Build workflow.
    """
    if not path.is_file():
        return 0
    lines = path.read_text(encoding="utf-8").splitlines()
    indexes = [i for i, line in enumerate(lines) if HOOK_USES in line and not line.lstrip().startswith("#")]
    changed = 0
    for idx in reversed(indexes):
        try:
            start, end, _ = step_bounds(lines, idx)
        except ValueError:
            continue
        # Trim one adjacent blank line to avoid accumulating whitespace.
        if start > 0 and not lines[start - 1].strip():
            start -= 1
        del lines[start:end]
        changed += 1
    if changed:
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return changed


def unexpected_hook_files(root: Path) -> list[str]:
    workflows = root / ".github/workflows"
    if not workflows.is_dir():
        return []
    allowed = set(TARGETS) | {FOXDESK_OWNED_WORKFLOW}
    found: list[str] = []
    for path in sorted(list(workflows.glob("*.yml")) + list(workflows.glob("*.yaml"))):
        rel = path.relative_to(root).as_posix()
        if rel in allowed:
            continue
        if HOOK_USES in path.read_text(encoding="utf-8", errors="ignore"):
            found.append(rel)
    return found


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Instala ou valida hooks FoxxDesk nos workflows upstream")
    p.add_argument("--target", default=".")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.target).expanduser().resolve()
    if args.apply:
        installed = 0
        removed = 0
        for rel in TARGETS:
            installed += install_hooks(root / rel)
        workflows = root / ".github/workflows"
        if workflows.is_dir():
            allowed = set(TARGETS) | {FOXDESK_OWNED_WORKFLOW}
            for path in sorted(list(workflows.glob("*.yml")) + list(workflows.glob("*.yaml"))):
                rel = path.relative_to(root).as_posix()
                if rel not in allowed:
                    removed += remove_hook_steps(path)
        print(f"FoxxDesk CI hooks OK: {installed} instalado(s), {removed} hook(s) legado(s) removido(s) ({SCRIPT_VERSION})")
        return 0

    errors: list[str] = []
    for rel in TARGETS:
        path = root / rel
        if not path.exists():
            # Some upstream versions may not ship every workflow; absence is not an error.
            continue
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        checkouts = active_checkout_indexes(lines)
        if not checkouts:
            errors.append(f"{rel}: workflow existe, mas nenhum actions/checkout ativo foi encontrado; atualização upstream exige revisão do hook")
            continue
        missing = missing_hooks(path)
        if missing:
            errors.append(f"{rel}: checkout(s) sem prepare nas linhas {', '.join(map(str, missing))}")
    for rel in unexpected_hook_files(root):
        errors.append(f"{rel}: contém hook FoxxDesk legado fora do fluxo manual")
    if errors:
        print("Hooks de CI FoxxDesk inconsistentes. Rode `python scripts/foxxdesk_prepare.py --apply --yes --sync-deps` e faça commit:", file=sys.stderr)
        for e in errors:
            print(f" - {e}", file=sys.stderr)
        return 2
    print(f"FoxxDesk CI hooks OK ({SCRIPT_VERSION})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
