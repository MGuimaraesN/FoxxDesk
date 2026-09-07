#!/usr/bin/env python3
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
