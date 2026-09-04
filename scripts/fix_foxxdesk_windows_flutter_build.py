#!/usr/bin/env python3
"""
Fixes the FoxxDesk Windows Flutter build after the RustDesk -> FoxxDesk rebrand.
Run from the repository root:

  python scripts/fix_foxxdesk_windows_flutter_build.py

It patches:
- flutter-rust-bridge generated class compatibility (FoxxdeskImpl -> RustdeskImpl alias)
- GitHub Actions bridge workflow to apply that compatibility after generation
- a few Dart null-safety/type issues reported by the Windows build
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path.cwd()


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    if new in text:
        print(f"OK already patched: {path}")
        return
    if old not in text:
        raise SystemExit(f"Pattern not found in {path}: {old!r}")
    write(path, text.replace(old, new, 1))
    print(f"PATCHED: {path}")


# 1) Add a post-generation bridge compatibility fixer.
bridge_compat = r'''#!/usr/bin/env python3
"""Keep old Dart API name RustdeskImpl after FoxxDesk Cargo package rename.

flutter_rust_bridge derives the generated Dart implementation class from the
Cargo package name. After package name `rustdesk` -> `foxxdesk`, the generated
class may become `FoxxdeskImpl`, but the Flutter app still imports/uses the
stable internal API name `RustdeskImpl`.

Do not rename all app code blindly. Add a Dart typedef alias instead.
"""
from __future__ import annotations

import re
from pathlib import Path

p = Path("flutter/lib/generated_bridge.dart")
if not p.exists():
    raise SystemExit(f"Missing generated bridge: {p}")

s = p.read_text(encoding="utf-8")

if "class RustdeskImpl" in s or "typedef RustdeskImpl" in s:
    print("generated_bridge.dart already exposes RustdeskImpl")
    raise SystemExit(0)

classes = re.findall(r"class\s+([A-Za-z_][A-Za-z0-9_]*Impl)\b", s)
preferred = [c for c in classes if "foxx" in c.lower() or "desk" in c.lower()]
impl = preferred[0] if preferred else (classes[0] if classes else None)

if not impl:
    raise SystemExit("Could not find generated bridge implementation class ending with Impl")

alias = f"""

// FoxxDesk compatibility alias.
// Keep the Flutter source compatible with the original FoxxDesk internal FFI name.
typedef RustdeskImpl = {impl};
"""
p.write_text(s.rstrip() + alias + "\n", encoding="utf-8")
print(f"Added typedef RustdeskImpl = {impl};")
'''
write("scripts/fix_generated_bridge_compat.py", bridge_compat)
print("CREATED/UPDATED: scripts/fix_generated_bridge_compat.py")

# 2) Make the reusable bridge workflow patch generated_bridge.dart before upload.
bridge_yml = ".github/workflows/bridge.yml"
text = read(bridge_yml)
step = """
      - name: Patch FoxxDesk bridge compatibility
        shell: bash
        run: python3 scripts/fix_generated_bridge_compat.py
"""
if "Patch FoxxDesk bridge compatibility" not in text:
    marker = """      - name: Upload Artifact
        uses: actions/upload-artifact"""
    if marker not in text:
        raise SystemExit("Could not find Upload Artifact step in .github/workflows/bridge.yml")
    text = text.replace(marker, step + "\n" + marker, 1)
    write(bridge_yml, text)
    print(f"PATCHED: {bridge_yml}")
else:
    print(f"OK already patched: {bridge_yml}")

# 3) Make local build.py generation apply the same alias whenever it touches generated_bridge.dart.
build_py = "build.py"
text = read(build_py)
old = '''def ffi_bindgen_function_refactor():
    # workaround ffigen
    system2(
        'sed -i "s/ffi.NativeFunction<ffi.Bool Function(DartPort/ffi.NativeFunction<ffi.Uint8 Function(DartPort/g" flutter/lib/generated_bridge.dart')
'''
new = '''def ffi_bindgen_function_refactor():
    # workaround ffigen
    system2(
        'sed -i "s/ffi.NativeFunction<ffi.Bool Function(DartPort/ffi.NativeFunction<ffi.Uint8 Function(DartPort/g" flutter/lib/generated_bridge.dart')
    if os.path.exists("scripts/fix_generated_bridge_compat.py"):
        system2("python3 scripts/fix_generated_bridge_compat.py")
'''
if new not in text:
    if old not in text:
        print("WARN: build.py ffi_bindgen_function_refactor block not found; skipped")
    else:
        write(build_py, text.replace(old, new, 1))
        print(f"PATCHED: {build_py}")
else:
    print(f"OK already patched: {build_py}")

# 4) Dart null-safety/type patches reported by the Windows Flutter build.
# Patch every LastWindowPosition.loadFromString(pos) occurrence; there are multiple helpers.
common_path = "flutter/lib/common.dart"
common_text = read(common_path)
if "LastWindowPosition.loadFromString(pos);" in common_text:
    write(common_path, common_text.replace(
        "LastWindowPosition.loadFromString(pos);",
        "LastWindowPosition.loadFromString(pos ?? '');",
    ))
    print(f"PATCHED: {common_path} (all LastWindowPosition nullable pos calls)")
else:
    print(f"OK already patched: {common_path} (LastWindowPosition)")
replace_once(
    "flutter/lib/common/widgets/dialog.dart",
    "controller.text = osPassword;",
    "controller.text = osPassword ?? '';",
)
replace_once(
    "flutter/lib/desktop/widgets/remote_toolbar.dart",
    "final results = await Future.wait([",
    "final results = await Future.wait<bool?>([",
)

# Force String generic on _Radio calls in desktop settings to avoid Dart inferring dynamic.
dsp = "flutter/lib/desktop/pages/desktop_setting_page.dart"
text = read(dsp)
if "_Radio(context" in text:
    text = text.replace("_Radio(context", "_Radio<String>(context")
    write(dsp, text)
    print(f"PATCHED: {dsp} (_Radio<String>)")
else:
    print(f"OK already patched: {dsp} (_Radio<String>)")

# Null bool fixes in toolbar around follow/show remote cursor.
toolbar = "flutter/lib/common/widgets/toolbar.dart"
text = read(toolbar)
repls = {
    """                state.value = bind.sessionGetToggleOptionSync(
                    sessionId: sessionId, arg: option);""": """                state.value = bind.sessionGetToggleOptionSync(
                        sessionId: sessionId, arg: option) ??
                    false;""",
    """    final value =
        bind.sessionGetToggleOptionSync(sessionId: sessionId, arg: option);""": """    final value =
            bind.sessionGetToggleOptionSync(sessionId: sessionId, arg: option) ??
        false;""",
    """    final showCursorEnabled = bind.sessionGetToggleOptionSync(
        sessionId: sessionId, arg: showCursorOption);""": """    final showCursorEnabled =
        bind.sessionGetToggleOptionSync(sessionId: sessionId, arg: showCursorOption) ??
            false;""",
    """      showCursorState.value = bind.sessionGetToggleOptionSync(
          sessionId: sessionId, arg: showCursorOption);""": """      showCursorState.value = bind.sessionGetToggleOptionSync(
              sessionId: sessionId, arg: showCursorOption) ??
          false;""",
    """          value = bind.sessionGetToggleOptionSync(
              sessionId: sessionId, arg: option);""": """          value = bind.sessionGetToggleOptionSync(
                  sessionId: sessionId, arg: option) ??
              false;""",
    """            showCursorState.value = bind.sessionGetToggleOptionSync(
                sessionId: sessionId, arg: showCursorOption);""": """            showCursorState.value = bind.sessionGetToggleOptionSync(
                    sessionId: sessionId, arg: showCursorOption) ??
                false;""",
    """        peerState.value =
            bind.sessionGetToggleOptionSync(sessionId: sessionId, arg: option);""": """        peerState.value =
                bind.sessionGetToggleOptionSync(sessionId: sessionId, arg: option) ??
            false;""",
}
changed = False
for old, new in repls.items():
    if old in text and new not in text:
        text = text.replace(old, new, 1)
        changed = True
if changed:
    write(toolbar, text)
    print(f"PATCHED: {toolbar}")
else:
    print(f"OK/no matching toolbar patches needed: {toolbar}")

print("\nDone. Now run:")
print("  flutter clean")
print("  flutter pub get")
print("  flutter build windows --release")
print("or push and rerun GitHub Actions.")
