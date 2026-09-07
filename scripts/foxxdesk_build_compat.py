#!/usr/bin/env python3
"""Apply/check narrow FoxxDesk build compatibility patches.

This helper intentionally patches only build/package integration points that are
known to break after public branding. It never replaces whole upstream files.

Owned invariants:
- macOS Flutter bundle path is discovered dynamically (no hardcoded RustDesk.app)
- Flutter RPM specs install/package the bundle from one consistent /usr/share/foxxdesk path
- GitHub release publication is opt-in and independent from Actions artifact upload
- upstream Flutter Nightly schedule is disabled when manual_build_only=true
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from foxxdesk_config import load_config  # noqa: E402

SCRIPT_VERSION = "foxxdesk-build-compat-v1-2026-09-06"
RELEASE_ACTION = "softprops/action-gh-release@"
RELEASE_GATE = "env.FOXXDESK_PUBLISH_RELEASE == 'true'"


class CompatError(RuntimeError):
    pass


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_if_changed(path: Path, before: str, after: str, *, apply: bool) -> bool:
    if before == after:
        return False
    if apply:
        path.write_text(after, encoding="utf-8", newline="\n")
    return True


def patch_build_py(text: str) -> str:
    marker = "def resolve_flutter_macos_app_bundle() -> Path:"
    if marker not in text:
        anchor = "\ndef get_deb_arch() -> str:\n"
        if anchor not in text:
            raise CompatError("build.py: anchor get_deb_arch() não encontrado")
        helper = r'''

def resolve_flutter_macos_app_bundle() -> Path:
    """Return the actual Flutter .app bundle without assuming the upstream name."""
    release_dir = Path("build/macos/Build/Products/Release")
    preferred = release_dir / f"{APP_DISPLAY_NAME}.app"
    if preferred.is_dir():
        return preferred
    apps = sorted(p for p in release_dir.glob("*.app") if p.is_dir())
    if len(apps) == 1:
        return apps[0]
    names = ", ".join(p.name for p in apps) if apps else "nenhum"
    raise RuntimeError(
        f"Não foi possível identificar o bundle macOS em {release_dir}: {names}. "
        "O Flutter deve gerar exatamente um .app ou APP_DISPLAY_NAME deve corresponder ao produto."
    )
'''
        text = text.replace(anchor, helper + anchor, 1)

    old = "    system2('cp -rf ../target/release/service ./build/macos/Build/Products/Release/RustDesk.app/Contents/MacOS/')"
    if old in text:
        new = """    mac_app = resolve_flutter_macos_app_bundle()\n    service_src = Path('../target/release/service')\n    service_dst = mac_app / 'Contents' / 'MacOS' / 'service'\n    service_dst.parent.mkdir(parents=True, exist_ok=True)\n    shutil.copy2(service_src, service_dst)"""
        text = text.replace(old, new, 1)

    # Older FoxxDesk variants may already hardcode FoxxDesk.app. Replace that too
    # so custom display names and future upstream PRODUCT_NAME changes keep working.
    old_foxx = "    system2('cp -rf ../target/release/service ./build/macos/Build/Products/Release/FoxxDesk.app/Contents/MacOS/')"
    if old_foxx in text:
        new = """    mac_app = resolve_flutter_macos_app_bundle()\n    service_src = Path('../target/release/service')\n    service_dst = mac_app / 'Contents' / 'MacOS' / 'service'\n    service_dst.parent.mkdir(parents=True, exist_ok=True)\n    shutil.copy2(service_src, service_dst)"""
        text = text.replace(old_foxx, new, 1)

    return text


def patch_rpm_flutter_spec(text: str, label: str) -> str:
    # Keep the internal executable name rustdesk for upstream/runtime compatibility,
    # but install the complete Flutter bundle under the FoxxDesk-owned data root.
    text = text.replace(
        'mkdir -p "%{buildroot}/usr/share/rustdesk" && cp -r ${HBB}/flutter/build/linux/x64/release/bundle/* -t "%{buildroot}/usr/share/rustdesk"',
        'mkdir -p "%{buildroot}/usr/share/foxxdesk" && cp -r ${HBB}/flutter/build/linux/x64/release/bundle/* -t "%{buildroot}/usr/share/foxxdesk"',
    )

    m = re.search(r"(?ms)^%files\s*\n(.*?)(?=^%changelog\s*$)", text)
    if not m:
        raise CompatError(f"{label}: bloco %files não encontrado")
    block = m.group(1)
    # Preserve non-FoxxDesk entries (icons etc.) but own /usr/share/foxxdesk once,
    # recursively, avoiding both unpackaged files and duplicate file warnings.
    keep: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('/usr/share/foxxdesk'):
            continue
        keep.append(line)
    new_lines = ['/usr/share/foxxdesk'] + keep
    new_block = "\n".join(new_lines) + "\n\n"
    text = text[:m.start(1)] + new_block + text[m.end(1):]
    return text


def step_bounds(lines: list[str], uses_idx: int) -> tuple[int, int]:
    uses_indent = len(lines[uses_idx]) - len(lines[uses_idx].lstrip(' '))
    step_indent = max(0, uses_indent - 2)
    start = uses_idx
    while start >= 0:
        line = lines[start]
        if (len(line) - len(line.lstrip(' '))) == step_indent and line.lstrip().startswith('- '):
            break
        start -= 1
    if start < 0:
        raise CompatError(f"flutter-build.yml: início do step de release não localizado na linha {uses_idx + 1}")
    end = uses_idx + 1
    while end < len(lines):
        line = lines[end]
        if line.strip():
            indent = len(line) - len(line.lstrip(' '))
            if indent < step_indent:
                break
            if indent == step_indent and line.lstrip().startswith('- '):
                break
        end += 1
    return start, end


def ensure_workflow_call_input(text: str) -> str:
    # Only patch the workflow_call input header. Never search globally for upload-tag,
    # because the same key appears later in callers/steps.
    if re.search(r"(?m)^      publish-release:\s*$", text):
        return text
    anchor = """      upload-tag:
        type: string
        default: "nightly"
"""
    if anchor not in text:
        raise CompatError("flutter-build.yml: bloco workflow_call upload-tag não encontrado")
    addition = anchor + """      publish-release:
        type: boolean
        default: false
"""
    return text.replace(anchor, addition, 1)

def patch_flutter_build_workflow(text: str) -> str:
    text = ensure_workflow_call_input(text)
    if not re.search(r"(?m)^\s{2}FOXXDESK_PUBLISH_RELEASE:\s*", text):
        anchor = re.search(r'(?m)^(\s{2}UPLOAD_ARTIFACT:\s*.*)$', text)
        if not anchor:
            raise CompatError("flutter-build.yml: env UPLOAD_ARTIFACT não encontrado")
        line = '  FOXXDESK_PUBLISH_RELEASE: "${{ inputs.publish-release }}"'
        text = text[:anchor.end()] + "\n" + line + text[anchor.end():]

    lines = text.splitlines()
    indexes = [i for i, line in enumerate(lines) if RELEASE_ACTION in line and not line.lstrip().startswith('#')]
    for idx in reversed(indexes):
        start, end = step_bounds(lines, idx)
        if_idx = None
        for j in range(start, end):
            if re.match(r"^\s+if:\s*", lines[j]):
                if_idx = j
                break
        if if_idx is None:
            indent = ' ' * (len(lines[idx]) - len(lines[idx].lstrip(' ')))
            lines.insert(idx, f"{indent}if: {RELEASE_GATE}")
        elif RELEASE_GATE not in lines[if_idx]:
            current = lines[if_idx]
            prefix, expr = current.split('if:', 1)
            expr = expr.strip()
            if expr.startswith('${{') and expr.endswith('}}'):
                expr = expr[3:-2].strip()
            lines[if_idx] = f"{prefix}if: {expr} && {RELEASE_GATE}"
    return "\n".join(lines).rstrip() + "\n"


def patch_foxxdesk_build_workflow(text: str, publish_default: bool) -> str:
    # workflow_dispatch input block
    if not re.search(r"(?m)^      publish_release:\s*$", text):
        anchor = """      upload_tag:
        description: "Release tag used for prerelease upload"
        required: true
        type: string
        default: "foxxdesk-nightly"
"""
        if anchor not in text:
            raise CompatError("foxxdesk-build.yml: bloco workflow_dispatch upload_tag não encontrado")
        addition = anchor + (
            "      publish_release:\n"
            "        description: \"Create/update a GitHub prerelease (requires contents: write)\"\n"
            "        required: true\n"
            "        type: boolean\n"
            f"        default: {'true' if publish_default else 'false'}\n"
        )
        text = text.replace(anchor, addition, 1)

    # reusable-workflow argument block
    if "      publish-release: ${{ inputs.publish_release }}" not in text:
        anchor = "      upload-tag: ${{ inputs.upload_tag }}"
        if anchor not in text:
            raise CompatError("foxxdesk-build.yml: passagem upload-tag não encontrada")
        text = text.replace(anchor, anchor + "\n      publish-release: ${{ inputs.publish_release }}", 1)
    return text

def patch_flutter_tag_workflow(text: str) -> str:
    # Tag builds are the one upstream path where release publication is expected.
    if not re.search(r"(?m)^permissions:\s*$", text):
        marker = "\njobs:\n"
        if marker not in text:
            raise CompatError("flutter-tag.yml: jobs anchor não encontrado")
        text = text.replace(marker, "\npermissions:\n  contents: write\n  actions: read\n" + marker, 1)
    if not re.search(r"(?m)^\s{6}publish-release:\s*true\s*$", text):
        anchor = re.search(r"(?m)^(\s{6}upload-tag:\s*\$\{\{ github\.ref_name \}\}\s*)$", text)
        if not anchor:
            raise CompatError("flutter-tag.yml: upload-tag anchor não encontrado")
        text = text[:anchor.end()] + "\n      publish-release: true" + text[anchor.end():]
    return text


def patch_flutter_nightly(text: str, disable_schedule: bool) -> str:
    if not disable_schedule:
        return text
    # Parse line-by-line and remove only the schedule key and its indented body.
    # Preserve workflow_dispatch and every job exactly as upstream provided it.
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i] == '  schedule:':
            i += 1
            while i < len(lines):
                line = lines[i]
                if line and (len(line) - len(line.lstrip(' '))) <= 2:
                    break
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out).rstrip() + "\n"

def check_invariants(root: Path, cfg: dict) -> list[str]:
    errors: list[str] = []

    build_py = root / 'build.py'
    if not build_py.is_file():
        errors.append('build.py ausente')
    else:
        t = read(build_py)
        if 'def resolve_flutter_macos_app_bundle() -> Path:' not in t:
            errors.append('build.py: resolvedor dinâmico de .app macOS ausente')
        if re.search(r"cp -rf ../target/release/service .*Release/(?:RustDesk|FoxxDesk)\.app/Contents/MacOS", t):
            errors.append('build.py: cópia de service ainda usa bundle macOS hardcoded')

    for rel in ('res/rpm-flutter.spec', 'res/rpm-flutter-suse.spec'):
        p = root / rel
        if not p.is_file():
            errors.append(f'{rel} ausente')
            continue
        t = read(p)
        if '%{buildroot}/usr/share/rustdesk' in t:
            errors.append(f'{rel}: Flutter bundle ainda é instalado em /usr/share/rustdesk')
        m = re.search(r"(?ms)^%files\s*\n(.*?)(?=^%changelog\s*$)", t)
        if not m or '/usr/share/foxxdesk' not in [x.strip() for x in m.group(1).splitlines()]:
            errors.append(f'{rel}: %files não possui /usr/share/foxxdesk recursivo')

    flutter = root / '.github/workflows/flutter-build.yml'
    if not flutter.is_file():
        errors.append('.github/workflows/flutter-build.yml ausente')
    else:
        t = read(flutter)
        if not re.search(r"(?m)^\s{6}publish-release:\s*$", t):
            errors.append('flutter-build.yml: input publish-release ausente')
        if 'FOXXDESK_PUBLISH_RELEASE:' not in t:
            errors.append('flutter-build.yml: env FOXXDESK_PUBLISH_RELEASE ausente')
        lines = t.splitlines()
        for i, line in enumerate(lines):
            if RELEASE_ACTION in line and not line.lstrip().startswith('#'):
                start, end = step_bounds(lines, i)
                block = '\n'.join(lines[start:end])
                if RELEASE_GATE not in block:
                    errors.append(f'flutter-build.yml: release action sem gate opt-in perto da linha {i + 1}')

    own = root / '.github/workflows/foxxdesk-build.yml'
    if own.is_file():
        t = read(own)
        if 'publish_release:' not in t or 'publish-release: ${{ inputs.publish_release }}' not in t:
            errors.append('foxxdesk-build.yml: opção publish_release não está conectada ao reusable workflow')

    if bool(cfg.get('github_actions', {}).get('manual_build_only', True)) and bool(cfg.get('github_actions', {}).get('disable_upstream_nightly_schedule', True)):
        nightly = root / '.github/workflows/flutter-nightly.yml'
        if nightly.is_file() and re.search(r"(?m)^\s{2}schedule:\s*$", read(nightly)):
            errors.append('flutter-nightly.yml: schedule automático ainda ativo')

    tag = root / '.github/workflows/flutter-tag.yml'
    if tag.is_file() and 'publish-release: true' in read(tag):
        tt = read(tag)
        if not re.search(r"(?ms)^permissions:\s*\n(?:  .*\n)*  contents:\s*write\s*$", tt):
            errors.append('flutter-tag.yml: release habilitada sem permissions.contents=write')

    return errors


def apply_or_check(root: Path, *, apply: bool) -> int:
    cfg, _ = load_config(root, migrate_legacy=True, write_migration=False)
    gha = cfg.get('github_actions', {})
    publish_default = bool(gha.get('publish_release_default', False))
    disable_nightly = bool(gha.get('disable_upstream_nightly_schedule', True))

    targets: list[tuple[Path, callable]] = [
        (root / 'build.py', patch_build_py),
        (root / 'res/rpm-flutter.spec', lambda t: patch_rpm_flutter_spec(t, 'res/rpm-flutter.spec')),
        (root / 'res/rpm-flutter-suse.spec', lambda t: patch_rpm_flutter_spec(t, 'res/rpm-flutter-suse.spec')),
        (root / '.github/workflows/flutter-build.yml', patch_flutter_build_workflow),
        (root / '.github/workflows/foxxdesk-build.yml', lambda t: patch_foxxdesk_build_workflow(t, publish_default)),
    ]
    nightly = root / '.github/workflows/flutter-nightly.yml'
    if nightly.is_file():
        targets.append((nightly, lambda t: patch_flutter_nightly(t, disable_nightly)))
    tag = root / '.github/workflows/flutter-tag.yml'
    if tag.is_file():
        targets.append((tag, patch_flutter_tag_workflow))

    changed = 0
    if apply:
        for path, fn in targets:
            if not path.is_file():
                raise CompatError(f'arquivo obrigatório ausente: {path.relative_to(root)}')
            before = read(path)
            after = fn(before)
            changed += int(write_if_changed(path, before, after, apply=True))

    errors = check_invariants(root, cfg)
    if errors:
        raise CompatError('; '.join(errors))
    mode = 'apply' if apply else 'check'
    print(f'FoxxDesk build compatibility OK: {changed} arquivo(s) alterado(s) ({SCRIPT_VERSION}, {mode})')
    return changed


def main() -> int:
    p = argparse.ArgumentParser(description='Aplica/valida compatibilidade de build FoxxDesk sem substituir arquivos upstream inteiros')
    p.add_argument('--target', default='.')
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = p.parse_args()
    root = Path(args.target).expanduser().resolve()
    try:
        apply_or_check(root, apply=args.apply)
    except Exception as exc:
        print(f'ERRO build compat: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
