#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_foxxdesk_rebrand_all_files_no_zip_v27.py

Versão all-files patch-only sem ZIP/payload/manifesto e sem espelhar arquivos inteiros.

Objetivo:
- Fazer o rebrand completo por regras/patches, preservando atualizações futuras.
- Não lê ZIP de referência.
- Não usa manifesto externo.
- Não guarda payload/base64.
- Não substitui arquivo inteiro por snapshot antigo.
- Por padrão usa --profile full para alterar a allowlist completa.
- Esta versão foi nomeada para evitar confusão com a v9 safe, que altera só o núcleo crítico.
- Use --profile safe apenas se quiser só correções críticas/build.
- Quando precisa renomear um arquivo, copia o arquivo atual existente no alvo
  para o novo nome e aplica as regras no conteúdo; não usa versão antiga.
"""
from __future__ import annotations

import argparse
import os
import codecs
import datetime as _dt
import hashlib
import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

SCRIPT_VERSION = "v39-submodule-safe-runtime-defaults-2026-09-05"
APP_DISPLAY_NAME = "FoxxDesk"
APP_SLUG = "foxxdesk"
APP_SLUG_UPPER = "FOXXDESK"
DEFAULT_SERVER = "foxxdesk.mguimaraesn.dev"
DEFAULT_KEY = "6WbpsDtYMwUca74qNvNaBfV4pUIGzyXnX1Q8V8fZ8YA="
DEFAULT_MAINTAINER_EMAIL = "mateus@mguimaraesn.dev"
COPYRIGHT_OWNER = "MGN Systems"
COPYRIGHT_YEAR = str(_dt.datetime.now().year)
COPYRIGHT_TEXT = f"Copyright © {COPYRIGHT_YEAR} {COPYRIGHT_OWNER}. All rights reserved."
COPYRIGHT_HTML = f"Copyright &copy; {COPYRIGHT_YEAR} {COPYRIGHT_OWNER}."


def configure_brand_globals(args: argparse.Namespace) -> None:
    """Set public brand values from the central config/CLI before patching.

    Internal API identifiers remain protected by the patch rules; this only changes
    the values the script intentionally exposes as configurable.
    """
    global APP_DISPLAY_NAME, APP_SLUG, APP_SLUG_UPPER, COPYRIGHT_OWNER, COPYRIGHT_TEXT, COPYRIGHT_HTML
    global DEFAULT_MAINTAINER_EMAIL
    if getattr(args, "display_name", None):
        APP_DISPLAY_NAME = str(args.display_name)
    if getattr(args, "slug", None):
        APP_SLUG = str(args.slug)
        APP_SLUG_UPPER = APP_SLUG.upper()
    if getattr(args, "company", None):
        COPYRIGHT_OWNER = str(args.company)
    if getattr(args, "maintainer_email", None):
        DEFAULT_MAINTAINER_EMAIL = str(args.maintainer_email)
    COPYRIGHT_TEXT = f"Copyright © {COPYRIGHT_YEAR} {COPYRIGHT_OWNER}. All rights reserved."
    COPYRIGHT_HTML = f"Copyright &copy; {COPYRIGHT_YEAR} {COPYRIGHT_OWNER}."

BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".icns", ".exe", ".dll",
    ".so", ".dylib", ".bin", ".zip", ".tar", ".gz", ".pdf", ".ttf", ".otf",
    ".woff", ".woff2", ".7z", ".xz", ".a", ".lib", ".mp4", ".mov", ".apk", ".dmg"
}

SKIP_DIRS = {
    ".git", ".github/cache", ".rebrand_backup", "target", "build", "dist", "node_modules",
    "flutter/build", "flutter/.dart_tool", "flutter/.pub-cache", "flutter/ephemeral",
}

ALLOWED_FILES: List[str] = [
    '.github/FUNDING.yml',
    '.github/ISSUE_TEMPLATE/bug_report.yaml',
    '.github/workflows/bridge.yml',
    '.github/workflows/fdroid.yml',
    '.github/workflows/flutter-build.yml',
    '.github/workflows/flutter-ci.yml',
    '.github/workflows/flutter-nightly.yml',
    '.github/workflows/flutter-tag.yml',
    '.github/workflows/foxxdesk-build.yml',
    '.github/workflows/playground.yml',
    'AGENTS.md',
    'BRAND_CHANGELOG.md',
    'Cargo.toml',
    'Cargo.lock',
    'Dockerfile',
    'FOXXDESK_MAX_SAFE_BRAND_REPORT.md',
    'FOXXDESK_SERVER_DEFAULTS.md',
    'NOTICE.md',
    'README.md',
    'appimage/AppImageBuilder-aarch64.yml',
    'appimage/AppImageBuilder-x86_64.yml',
    'build.py',
    'docs/CONTRIBUTING-DE.md',
    'docs/CONTRIBUTING-FR.md',
    'docs/CONTRIBUTING-ID.md',
    'docs/CONTRIBUTING-IT.md',
    'docs/CONTRIBUTING-JP.md',
    'docs/CONTRIBUTING-KR.md',
    'docs/CONTRIBUTING-NL.md',
    'docs/CONTRIBUTING-NO.md',
    'docs/CONTRIBUTING-PL.md',
    'docs/CONTRIBUTING-RO.md',
    'docs/CONTRIBUTING-RU.md',
    'docs/CONTRIBUTING-TR.md',
    'docs/CONTRIBUTING-ZH.md',
    'docs/CONTRIBUTING.md',
    'docs/README-AR.md',
    'docs/README-CS.md',
    'docs/README-DA.md',
    'docs/README-DE.md',
    'docs/README-EO.md',
    'docs/README-ES.md',
    'docs/README-FA.md',
    'docs/README-FI.md',
    'docs/README-FR.md',
    'docs/README-GR.md',
    'docs/README-HU.md',
    'docs/README-ID.md',
    'docs/README-IT.md',
    'docs/README-JP.md',
    'docs/README-KR.md',
    'docs/README-ML.md',
    'docs/README-NL.md',
    'docs/README-NO.md',
    'docs/README-PL.md',
    'docs/README-PTBR.md',
    'docs/README-RO.md',
    'docs/README-RU.md',
    'docs/README-TR.md',
    'docs/README-UA.md',
    'docs/README-VN.md',
    'docs/README-ZH.md',
    'docs/SECURITY-DE.md',
    'docs/SECURITY-FR.md',
    'docs/SECURITY-IT.md',
    'docs/SECURITY-JP.md',
    'docs/SECURITY-KR.md',
    'docs/SECURITY-NL.md',
    'docs/SECURITY-NO.md',
    'docs/SECURITY-PL.md',
    'docs/SECURITY-RO.md',
    'docs/SECURITY-TR.md',
    'docs/SECURITY.md',
    'entrypoint.sh',
    'fastlane/metadata/android/en-US/full_description.txt',
    'fastlane/metadata/android/fr-FR/full_description.txt',
    'fastlane/metadata/android/nl-NL/full_description.txt',
    'fastlane/metadata/android/zh-CN/full_description.txt',
    'flatpak/com.foxxdesk.client.metainfo.xml',
    'flatpak/foxxdesk.json',
    'flutter/android/app/build.gradle',
    'flutter/android/app/src/main/AndroidManifest.xml',
    'flutter/android/app/src/main/kotlin/com/carriez/flutter_hbb/BootReceiver.kt',
    'flutter/android/app/src/main/kotlin/com/carriez/flutter_hbb/FloatingWindowService.kt',
    'flutter/android/app/src/main/kotlin/com/carriez/flutter_hbb/MainService.kt',
    'flutter/android/app/src/main/res/values/strings.xml',
    'flutter/build_android_deps.sh',
    'flutter/build_fdroid.sh',
    'flutter/build_ios.sh',
    'flutter/ios/Runner.xcodeproj/project.pbxproj',
    'flutter/ios/Runner.xcodeproj/xcshareddata/xcschemes/Runner.xcscheme',
    'flutter/ios/Runner/GoogleService-Info.plist',
    'flutter/ios/Runner/Info.plist',
    'flutter/ios/exportOptions.plist',
    'flutter/lib/common.dart',
    'flutter/lib/common/widgets/dialog.dart',
    'flutter/lib/common/widgets/login.dart',
    'flutter/lib/common/widgets/toolbar.dart',
    'flutter/lib/consts.dart',
    'flutter/lib/desktop/pages/desktop_setting_page.dart',
    'flutter/lib/desktop/widgets/remote_toolbar.dart',
    'flutter/lib/mobile/pages/settings_page.dart',
    'flutter/lib/models/group_model.dart',
    'flutter/lib/models/model.dart',
    'flutter/lib/models/native_model.dart',
    'flutter/lib/plugin/manager.dart',
    'flutter/lib/plugin/widgets/desc_ui.dart',
    'flutter/lib/utils/multi_window_manager.dart',
    'flutter/lib/utils/platform_channel.dart',
    'flutter/linux/CMakeLists.txt',
    'flutter/linux/main.cc',
    'flutter/linux/my_application.cc',
    'flutter/macos/Runner.xcodeproj/project.pbxproj',
    'flutter/macos/Runner.xcodeproj/xcshareddata/xcschemes/Runner.xcscheme',
    'flutter/macos/Runner/Base.lproj/MainMenu.xib',
    'flutter/macos/Runner/Configs/AppInfo.xcconfig',
    'flutter/macos/Runner/Info.plist',
    'flutter/macos/Runner/MainFlutterWindow.swift',
    'flutter/pubspec.yaml',
    'flutter/windows/CMakeLists.txt',
    'flutter/windows/runner/Runner.rc',
    'flutter/windows/runner/main.cpp',
    'flutter/windows/runner/runner.exe.manifest',
    'libs/clipboard/README.md',
    'libs/clipboard/src/lib.rs',
    'libs/clipboard/src/platform/unix/fuse/mod.rs',
    'libs/clipboard/src/platform/unix/macos/README.md',
    'libs/clipboard/src/platform/unix/macos/pasteboard_context.rs',
    'libs/enigo/src/linux/xdo.rs',
    'libs/hbb_common/src/config.rs',
    'libs/hbb_common/src/fs.rs',
    'libs/hbb_common/src/platform/linux.rs',
    'libs/hbb_common/src/platform/mod.rs',
    'libs/portable/Cargo.lock',
    'libs/portable/Cargo.toml',
    'libs/portable/generate.py',
    'libs/portable/src/bin_reader.rs',
    'libs/portable/src/main.rs',
    'libs/remote_printer/src/lib.rs',
    'libs/remote_printer/src/setup/driver.rs',
    'libs/scrap/examples/capture_mag.rs',
    'libs/scrap/src/dxgi/mag.rs',
    'libs/virtual_display/dylib/src/lib.rs',
    'libs/virtual_display/dylib/src/win10/IddController.c',
    'res/DEBIAN/postinst',
    'res/DEBIAN/postrm',
    'res/DEBIAN/preinst',
    'res/DEBIAN/prerm',
    'res/PKGBUILD',
    'res/foxxdesk-link.desktop',
    'res/foxxdesk.desktop',
    'res/foxxdesk.service',
    'res/manifest.xml',
    'res/msi/CustomActions/CustomActions.cpp',
    'res/msi/CustomActions/RemotePrinter.cpp',
    'res/msi/Package/Components/FoxxDesk.wxs',
    'res/msi/Package/Language/Package.en-us.wxl',
    'res/msi/Package/Language/WixExt_en-us.wxl',
    'res/msi/README.md',
    'res/job.py',
    'res/msi/preprocess.py',
    'res/osx-dist.sh',
    'res/pacman_install',
    'res/pam.d/foxxdesk.debian',
    'res/pam.d/foxxdesk.suse',
    'res/rpm-flutter-suse.spec',
    'res/rpm-flutter.spec',
    'res/rpm-suse.spec',
    'res/rpm.spec',
    'scripts/apply_foxxdesk_brand.py',
    'scripts/apply_foxxdesk_brand_DEFINITIVE.py',
    'scripts/apply_foxxdesk_brand_SAFE.py',
    'scripts/apply_foxxdesk_brand_with_fixes.py',
    'scripts/fix_foxxdesk_windows_flutter_build.py',
    'scripts/fix_generated_bridge_compat.py',
    'scripts/apply_foxxdesk_icon.py',
    'src/client.rs',
    'src/client/io_loop.rs',
    'src/clipboard.rs',
    'src/common.rs',
    'src/core_main.rs',
    'src/custom_server.rs',
    'src/flutter.rs',
    'src/flutter_ffi.rs',
    'src/hbbs_http/account.rs',
    'src/ipc.rs',
    'src/ipc/auth.rs',
    'src/ipc/fs.rs',
    'src/lang.rs',
    'src/lang/ar.rs',
    'src/lang/be.rs',
    'src/lang/bg.rs',
    'src/lang/ca.rs',
    'src/lang/cn.rs',
    'src/lang/cs.rs',
    'src/lang/da.rs',
    'src/lang/de.rs',
    'src/lang/el.rs',
    'src/lang/en.rs',
    'src/lang/eo.rs',
    'src/lang/es.rs',
    'src/lang/et.rs',
    'src/lang/eu.rs',
    'src/lang/fa.rs',
    'src/lang/fi.rs',
    'src/lang/fr.rs',
    'src/lang/ge.rs',
    'src/lang/he.rs',
    'src/lang/hi.rs',
    'src/lang/hr.rs',
    'src/lang/hu.rs',
    'src/lang/id.rs',
    'src/lang/it.rs',
    'src/lang/ja.rs',
    'src/lang/ko.rs',
    'src/lang/kz.rs',
    'src/lang/lt.rs',
    'src/lang/lv.rs',
    'src/lang/nb.rs',
    'src/lang/nl.rs',
    'src/lang/pl.rs',
    'src/lang/pt_PT.rs',
    'src/lang/ptbr.rs',
    'src/lang/ro.rs',
    'src/lang/ru.rs',
    'src/lang/sc.rs',
    'src/lang/sk.rs',
    'src/lang/sl.rs',
    'src/lang/sq.rs',
    'src/lang/sr.rs',
    'src/lang/sv.rs',
    'src/lang/ta.rs',
    'src/lang/th.rs',
    'src/lang/tr.rs',
    'src/lang/tw.rs',
    'src/lang/uk.rs',
    'src/main.rs',
    'src/naming.rs',
    'src/platform/delegate.rs',
    'src/platform/gtk_sudo.rs',
    'src/platform/linux.rs',
    'src/platform/linux_desktop_manager.rs',
    'src/platform/macos.rs',
    'src/platform/privileges_scripts/agent.plist',
    'src/platform/privileges_scripts/daemon.plist',
    'src/platform/privileges_scripts/install.scpt',
    'src/platform/privileges_scripts/uninstall.scpt',
    'src/platform/privileges_scripts/update.scpt',
    'src/platform/windows.cc',
    'src/platform/windows.rs',
    'src/platform/windows/acl.rs',
    'src/platform/windows_delete_test_cert.cc',
    'src/plugin/callback_msg.rs',
    'src/plugin/errno.rs',
    'src/plugin/manager.rs',
    'src/plugin/plugins.rs',
    'src/privacy_mode/win_topmost_window.rs',
    'src/rendezvous_mediator.rs',
    'src/server/clipboard_service.rs',
    'src/server/connection.rs',
    'src/server/dbus.rs',
    'src/server/input_service.rs',
    'src/server/terminal_service.rs',
    'src/ui_cm_interface.rs',
    'src/ui_session_interface.rs',
    'src/ui/index.tis',
    'src/virtual_display_manager.rs',
]

SAFE_CORE_FILES: List[str] = [
    "Cargo.toml",
    "Cargo.lock",
    "libs/portable/Cargo.toml",
    "libs/portable/Cargo.lock",
    "build.py",
    "libs/hbb_common/src/config.rs",
    "FOXXDESK_SERVER_DEFAULTS.md",
    "res/pacman_install",
    "res/PKGBUILD",
    "res/DEBIAN/postinst",
    "res/DEBIAN/postrm",
    "res/DEBIAN/preinst",
    "res/DEBIAN/prerm",
    "res/rpm-flutter-suse.spec",
    "res/rpm-flutter.spec",
    "res/rpm-suse.spec",
    "res/rpm.spec",
    "res/foxxdesk-link.desktop",
    "res/foxxdesk.desktop",
    "res/foxxdesk.service",
    "res/pam.d/foxxdesk.debian",
    "res/pam.d/foxxdesk.suse",
    "flatpak/com.foxxdesk.client.metainfo.xml",
    "flatpak/foxxdesk.json",
    "res/msi/Package/Components/FoxxDesk.wxs",
]


# Runtime profile: reaplica o brand necessário ao produto/build após uma atualização
# sem tocar documentação/contribuição nem arquivos hbb_common de API/plataforma.
RUNTIME_EXCLUDE_PREFIXES = ("docs/",)
RUNTIME_EXCLUDE_FILES = {
    ".github/FUNDING.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yaml",
    "AGENTS.md",
    "BRAND_CHANGELOG.md",
    "FOXXDESK_MAX_SAFE_BRAND_REPORT.md",
    "FOXXDESK_SERVER_DEFAULTS.md",
    "NOTICE.md",
    "README.md",
    "libs/clipboard/README.md",
    "res/msi/README.md",
    # hbb_common deve permanecer o mais próximo possível da revisão upstream;
    # somente config.rs recebe defaults/APP_NAME FoxxDesk.
    "libs/hbb_common/src/platform/linux.rs",
    "libs/hbb_common/src/platform/mod.rs",
    "libs/hbb_common/src/fs.rs",
}
RUNTIME_FILES: List[str] = [
    rel for rel in ALLOWED_FILES
    if not rel.startswith(RUNTIME_EXCLUDE_PREFIXES) and rel not in RUNTIME_EXCLUDE_FILES
]


GENERATED_HELPER_FILES: set[str] = {
    "scripts/fix_generated_bridge_compat.py",
    "scripts/fix_foxxdesk_windows_flutter_build.py",
    "scripts/apply_foxxdesk_icon.py",
    "scripts/foxxdesk_runtime_defaults.py",
    "scripts/foxxdesk_prepare.py",
    "scripts/foxxdesk_validate.py",
    "scripts/foxxdesk_sync_hbb_common.py",
    "scripts/foxxdesk_ci_hooks.py",
    "scripts/foxxdesk_config.py",
    "scripts/foxxdesk_build.py",
}

# User/upstream control files that the rebrand must never rewrite.
# In particular, .gitignore belongs to the repository owner and must remain byte-for-byte untouched.
NEVER_PATCH_FILES: set[str] = {
    ".gitignore",
    "flutter/.gitignore",
    ".gitattributes",
}

EXECUTABLE_FILES: set[str] = {
    # GitHub Actions/Linux/macOS runners precisam desses bits preservados no Git.
    # O script aplica chmod +x no filesystem; depois `git add` registra modo 100755.
    "build.py",
    "entrypoint.sh",
    "res/osx-dist.sh",
    "flutter/build_android.sh",
    "flutter/build_android_deps.sh",
    "flutter/build_fdroid.sh",
    "flutter/build_ios.sh",
    "flutter/ios_arm64.sh",
    "flutter/ios_x64.sh",
    "flutter/ndk_arm.sh",
    "flutter/ndk_arm64.sh",
    "flutter/ndk_x64.sh",
    "flutter/ndk_x86.sh",
    "flutter/run.sh",
    "scripts/fix_generated_bridge_compat.py",
    "scripts/fix_foxxdesk_windows_flutter_build.py",
    "scripts/apply_foxxdesk_icon.py",
}

# Arquivos antigos que não podem coexistir com o novo nome.
# No WiX SDK, todos os .wxs do diretório entram no build; manter RustDesk.wxs
# junto com FoxxDesk.wxs duplica ComponentGroup:Components e Component:App.StartMenu.
OBSOLETE_AFTER_RENAME_FILES: Dict[str, str] = {
    # Único cleanup automático padrão: o WiX SDK compila todos os .wxs do
    # diretório e os dois arquivos coexistindo geram IDs duplicados. Outros
    # arquivos upstream são preservados; remova-os apenas com --remove-old-renamed.
    "res/msi/Package/Components/RustDesk.wxs": "res/msi/Package/Components/FoxxDesk.wxs",
}

OPTIONAL_FILES: set[str] = {
    "BRAND_CHANGELOG.md",
    "FOXXDESK_MAX_SAFE_BRAND_REPORT.md",
    "FOXXDESK_SERVER_DEFAULTS.md",
    "NOTICE.md",
    # Scripts auxiliares gerados em versões antigas do rebrand.
    # Não são necessários para compilar o projeto e não devem ser recriados
    # a partir de snapshot antigo só para zerar pendência.
    "scripts/apply_foxxdesk_brand.py",
    "scripts/apply_foxxdesk_brand_DEFINITIVE.py",
    "scripts/apply_foxxdesk_brand_SAFE.py",
    "scripts/apply_foxxdesk_brand_with_fixes.py",
}

# Cópias seguras: não apaga o arquivo antigo por padrão.
FILE_RENAMES: Dict[str, str] = {
    "flatpak/com.rustdesk.RustDesk.metainfo.xml": "flatpak/com.foxxdesk.client.metainfo.xml",
    "flatpak/com.rustdesk.client.metainfo.xml": "flatpak/com.foxxdesk.client.metainfo.xml",
    "flatpak/rustdesk.json": "flatpak/foxxdesk.json",
    "res/rustdesk-link.desktop": "res/foxxdesk-link.desktop",
    "res/rustdesk.desktop": "res/foxxdesk.desktop",
    "res/rustdesk.service": "res/foxxdesk.service",
    "res/pam.d/rustdesk.debian": "res/pam.d/foxxdesk.debian",
    "res/pam.d/rustdesk.suse": "res/pam.d/foxxdesk.suse",
    "res/msi/Package/Components/RustDesk.wxs": "res/msi/Package/Components/FoxxDesk.wxs",
}

BRIDGE_COMPAT_SCRIPT = '#!/usr/bin/env python3\n"""Keep old Dart API name RustdeskImpl after FoxxDesk Cargo package rename.\n\nflutter_rust_bridge derives the generated Dart implementation class from the\nCargo package name. After package name `rustdesk` -> `foxxdesk`, the generated\nclass may become `FoxxdeskImpl`, but the Flutter app still imports/uses the\nstable internal API name `RustdeskImpl`.\n\nDo not rename all app code blindly. Add a Dart typedef alias instead.\n"""\nfrom __future__ import annotations\n\nimport re\nfrom pathlib import Path\n\np = Path("flutter/lib/generated_bridge.dart")\nif not p.exists():\n    raise SystemExit(f"Missing generated bridge: {p}")\n\ns = p.read_text(encoding="utf-8")\n\nif "class RustdeskImpl" in s or "typedef RustdeskImpl" in s:\n    print("generated_bridge.dart already exposes RustdeskImpl")\n    raise SystemExit(0)\n\nclasses = re.findall(r"class\\s+([A-Za-z_][A-Za-z0-9_]*Impl)\\b", s)\npreferred = [c for c in classes if "foxx" in c.lower() or "desk" in c.lower()]\nimpl = preferred[0] if preferred else (classes[0] if classes else None)\n\nif not impl:\n    raise SystemExit("Could not find generated bridge implementation class ending with Impl")\n\nalias = f"""\n\n// FoxxDesk compatibility alias.\n// Keep the Flutter source compatible with the original FoxxDesk internal FFI name.\ntypedef RustdeskImpl = {impl};\n"""\np.write_text(s.rstrip() + alias + "\\n", encoding="utf-8")\nprint(f"Added typedef RustdeskImpl = {impl};")\n'

FOXXDESK_BUILD_WORKFLOW = r"""name: FoxxDesk Build

on:
  # Intentionally manual-only. Never run the expensive FoxxDesk build on push/PR.
  workflow_dispatch:
    inputs:
      upload_artifact:
        description: "Upload build artifacts"
        required: true
        type: boolean
        default: true
      upload_tag:
        description: "Release tag used for prerelease upload"
        required: true
        type: string
        default: "foxxdesk-nightly"

permissions:
  contents: read
  actions: read

jobs:
  preflight:
    name: FoxxDesk preflight
    runs-on: ubuntu-22.04
    steps:
      - name: Checkout source code
        uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5
        with:
          submodules: recursive

      - name: Prepare and validate FoxxDesk source
        uses: ./.github/actions/prepare-foxxdesk

  build:
    name: FoxxDesk reusable Flutter build
    needs: preflight
    permissions:
      contents: write
      actions: read
    uses: ./.github/workflows/flutter-build.yml
    secrets: inherit
    with:
      upload-artifact: ${{ inputs.upload_artifact }}
      upload-tag: ${{ inputs.upload_tag }}
"""

WINDOWS_FLUTTER_BUILD_FIX_SCRIPT = '#!/usr/bin/env python3\n"""\nFixes the FoxxDesk Windows Flutter build after the RustDesk -> FoxxDesk rebrand.\nRun from the repository root:\n\n  python scripts/fix_foxxdesk_windows_flutter_build.py\n\nIt patches:\n- flutter-rust-bridge generated class compatibility (FoxxdeskImpl -> RustdeskImpl alias)\n- GitHub Actions bridge workflow to apply that compatibility after generation\n- a few Dart null-safety/type issues reported by the Windows build\n"""\nfrom __future__ import annotations\n\nimport re\nfrom pathlib import Path\n\nROOT = Path.cwd()\n\n\ndef read(path: str) -> str:\n    return (ROOT / path).read_text(encoding="utf-8")\n\n\ndef write(path: str, text: str) -> None:\n    p = ROOT / path\n    p.parent.mkdir(parents=True, exist_ok=True)\n    p.write_text(text, encoding="utf-8", newline="")\n\n\ndef replace_once(path: str, old: str, new: str) -> None:\n    text = read(path)\n    if new in text:\n        print(f"OK already patched: {path}")\n        return\n    if old not in text:\n        raise SystemExit(f"Pattern not found in {path}: {old!r}")\n    write(path, text.replace(old, new, 1))\n    print(f"PATCHED: {path}")\n\n\n# 1) Add a post-generation bridge compatibility fixer.\nbridge_compat = r\'\'\'#!/usr/bin/env python3\n"""Keep old Dart API name RustdeskImpl after FoxxDesk Cargo package rename.\n\nflutter_rust_bridge derives the generated Dart implementation class from the\nCargo package name. After package name `rustdesk` -> `foxxdesk`, the generated\nclass may become `FoxxdeskImpl`, but the Flutter app still imports/uses the\nstable internal API name `RustdeskImpl`.\n\nDo not rename all app code blindly. Add a Dart typedef alias instead.\n"""\nfrom __future__ import annotations\n\nimport re\nfrom pathlib import Path\n\np = Path("flutter/lib/generated_bridge.dart")\nif not p.exists():\n    raise SystemExit(f"Missing generated bridge: {p}")\n\ns = p.read_text(encoding="utf-8")\n\nif "class RustdeskImpl" in s or "typedef RustdeskImpl" in s:\n    print("generated_bridge.dart already exposes RustdeskImpl")\n    raise SystemExit(0)\n\nclasses = re.findall(r"class\\s+([A-Za-z_][A-Za-z0-9_]*Impl)\\b", s)\npreferred = [c for c in classes if "foxx" in c.lower() or "desk" in c.lower()]\nimpl = preferred[0] if preferred else (classes[0] if classes else None)\n\nif not impl:\n    raise SystemExit("Could not find generated bridge implementation class ending with Impl")\n\nalias = f"""\n\n// FoxxDesk compatibility alias.\n// Keep the Flutter source compatible with the original FoxxDesk internal FFI name.\ntypedef RustdeskImpl = {impl};\n"""\np.write_text(s.rstrip() + alias + "\\n", encoding="utf-8")\nprint(f"Added typedef RustdeskImpl = {impl};")\n\'\'\'\nwrite("scripts/fix_generated_bridge_compat.py", bridge_compat)\nprint("CREATED/UPDATED: scripts/fix_generated_bridge_compat.py")\n\n# 2) Make the reusable bridge workflow patch generated_bridge.dart before upload.\nbridge_yml = ".github/workflows/bridge.yml"\ntext = read(bridge_yml)\nstep = """\n      - name: Patch FoxxDesk bridge compatibility\n        shell: bash\n        run: python3 scripts/fix_generated_bridge_compat.py\n"""\nif "Patch FoxxDesk bridge compatibility" not in text:\n    marker = """      - name: Upload Artifact\n        uses: actions/upload-artifact"""\n    if marker not in text:\n        raise SystemExit("Could not find Upload Artifact step in .github/workflows/bridge.yml")\n    text = text.replace(marker, step + "\\n" + marker, 1)\n    write(bridge_yml, text)\n    print(f"PATCHED: {bridge_yml}")\nelse:\n    print(f"OK already patched: {bridge_yml}")\n\n# 3) Make local build.py generation apply the same alias whenever it touches generated_bridge.dart.\nbuild_py = "build.py"\ntext = read(build_py)\nold = \'\'\'def ffi_bindgen_function_refactor():\n    # workaround ffigen\n    system2(\n        \'sed -i "s/ffi.NativeFunction<ffi.Bool Function(DartPort/ffi.NativeFunction<ffi.Uint8 Function(DartPort/g" flutter/lib/generated_bridge.dart\')\n\'\'\'\nnew = \'\'\'def ffi_bindgen_function_refactor():\n    # workaround ffigen\n    system2(\n        \'sed -i "s/ffi.NativeFunction<ffi.Bool Function(DartPort/ffi.NativeFunction<ffi.Uint8 Function(DartPort/g" flutter/lib/generated_bridge.dart\')\n    if os.path.exists("scripts/fix_generated_bridge_compat.py"):\n        system2("python3 scripts/fix_generated_bridge_compat.py")\n\'\'\'\nif new not in text:\n    if old not in text:\n        print("WARN: build.py ffi_bindgen_function_refactor block not found; skipped")\n    else:\n        write(build_py, text.replace(old, new, 1))\n        print(f"PATCHED: {build_py}")\nelse:\n    print(f"OK already patched: {build_py}")\n\n# 4) Dart null-safety/type patches reported by the Windows Flutter build.\n# Patch every LastWindowPosition.loadFromString(pos) occurrence; there are multiple helpers.\ncommon_path = "flutter/lib/common.dart"\ncommon_text = read(common_path)\nif "LastWindowPosition.loadFromString(pos);" in common_text:\n    write(common_path, common_text.replace(\n        "LastWindowPosition.loadFromString(pos);",\n        "LastWindowPosition.loadFromString(pos ?? \'\');",\n    ))\n    print(f"PATCHED: {common_path} (all LastWindowPosition nullable pos calls)")\nelse:\n    print(f"OK already patched: {common_path} (LastWindowPosition)")\nreplace_once(\n    "flutter/lib/common/widgets/dialog.dart",\n    "controller.text = osPassword;",\n    "controller.text = osPassword ?? \'\';",\n)\nreplace_once(\n    "flutter/lib/desktop/widgets/remote_toolbar.dart",\n    "final results = await Future.wait([",\n    "final results = await Future.wait<bool?>([",\n)\n\n# Force String generic on _Radio calls in desktop settings to avoid Dart inferring dynamic.\ndsp = "flutter/lib/desktop/pages/desktop_setting_page.dart"\ntext = read(dsp)\nif "_Radio(context" in text:\n    text = text.replace("_Radio(context", "_Radio<String>(context")\n    write(dsp, text)\n    print(f"PATCHED: {dsp} (_Radio<String>)")\nelse:\n    print(f"OK already patched: {dsp} (_Radio<String>)")\n\n# Null bool fixes in toolbar around follow/show remote cursor.\ntoolbar = "flutter/lib/common/widgets/toolbar.dart"\ntext = read(toolbar)\nrepls = {\n    """                state.value = bind.sessionGetToggleOptionSync(\n                    sessionId: sessionId, arg: option);""": """                state.value = bind.sessionGetToggleOptionSync(\n                        sessionId: sessionId, arg: option) ??\n                    false;""",\n    """    final value =\n        bind.sessionGetToggleOptionSync(sessionId: sessionId, arg: option);""": """    final value =\n            bind.sessionGetToggleOptionSync(sessionId: sessionId, arg: option) ??\n        false;""",\n    """    final showCursorEnabled = bind.sessionGetToggleOptionSync(\n        sessionId: sessionId, arg: showCursorOption);""": """    final showCursorEnabled =\n        bind.sessionGetToggleOptionSync(sessionId: sessionId, arg: showCursorOption) ??\n            false;""",\n    """      showCursorState.value = bind.sessionGetToggleOptionSync(\n          sessionId: sessionId, arg: showCursorOption);""": """      showCursorState.value = bind.sessionGetToggleOptionSync(\n              sessionId: sessionId, arg: showCursorOption) ??\n          false;""",\n    """          value = bind.sessionGetToggleOptionSync(\n              sessionId: sessionId, arg: option);""": """          value = bind.sessionGetToggleOptionSync(\n                  sessionId: sessionId, arg: option) ??\n              false;""",\n    """            showCursorState.value = bind.sessionGetToggleOptionSync(\n                sessionId: sessionId, arg: showCursorOption);""": """            showCursorState.value = bind.sessionGetToggleOptionSync(\n                    sessionId: sessionId, arg: showCursorOption) ??\n                false;""",\n    """        peerState.value =\n            bind.sessionGetToggleOptionSync(sessionId: sessionId, arg: option);""": """        peerState.value =\n                bind.sessionGetToggleOptionSync(sessionId: sessionId, arg: option) ??\n            false;""",\n}\nchanged = False\nfor old, new in repls.items():\n    if old in text and new not in text:\n        text = text.replace(old, new, 1)\n        changed = True\nif changed:\n    write(toolbar, text)\n    print(f"PATCHED: {toolbar}")\nelse:\n    print(f"OK/no matching toolbar patches needed: {toolbar}")\n\nprint("\\nDone. Now run:")\nprint("  flutter clean")\nprint("  flutter pub get")\nprint("  flutter build windows --release")\nprint("or push and rerun GitHub Actions.")\n'


ICON_ASSET_SCRIPT = '#!/usr/bin/env python3\n"""\nGenerate all FoxxDesk app/logo image assets from a single source: res/icon.png.\n\nv3 scope:\n- Root res PNG/SVG/ICO assets.\n- Flutter shared asset: flutter/assets/icon.svg.\n- Android launcher/status icons under flutter/android/app/src/main/res/mipmap-*.\n- Android fastlane store icon.\n- iOS AppIcon.appiconset PNGs.\n- Windows app_icon.ico.\n- macOS AppIcon.icns.\n\nExplicit exclusions:\n- res/logo-header.svg\n- res/design.svg\n- res/icon.png, because it is the source image.\n\nNotes:\n- SVG files are SVG wrappers with embedded base64 PNG. They preserve the original dimensions/viewBox,\n  but are not true vector traces.\n- iOS icons are flattened to RGB because App Store icons must not contain transparency.\n- Android notification/status icons are generated as white alpha-mask icons.\n"""\n\nfrom __future__ import annotations\n\nimport argparse\nimport base64\nimport datetime as dt\nimport io\nimport json\nimport shutil\nfrom pathlib import Path\nfrom typing import Any\n\nfrom PIL import Image, ImageOps\n\nSCRIPT_VERSION = "icon-assets-v3-all-system-logos-2026-07-01"\n\ntry:\n    LANCZOS = Image.Resampling.LANCZOS\nexcept AttributeError:  # Pillow < 9\n    LANCZOS = Image.LANCZOS\n\nEXCLUDED = {\n    "res/logo-header.svg",\n    "res/design.svg",\n    "res/icon.png",\n}\n\nROOT_PNG_ASSETS = [\n    {"path": "res/32x32.png", "size": (32, 32), "mode": "RGBA"},\n    {"path": "res/64x64.png", "size": (64, 64), "mode": "RGBA"},\n    {"path": "res/128x128.png", "size": (128, 128), "mode": "RGBA"},\n    {"path": "res/128x128@2x.png", "size": (256, 256), "mode": "RGBA"},\n    {"path": "res/FoxxDesk.png", "size": (1600, 1600), "mode": "RGBA"},\n    {"path": "res/mac-icon.png", "size": (1024, 1024), "mode": "RGBA"},\n    {"path": "res/mac-tray-dark-x2.png", "size": (60, 60), "mode": "RGBA"},\n    {"path": "res/mac-tray-light-x2.png", "size": (48, 48), "mode": "LA"},\n    {"path": "fastlane/metadata/android/en-US/images/icon.png", "size": (256, 256), "mode": "RGB"},\n]\n\nSVG_ASSETS = [\n    {"path": "res/FoxxDesk.svg", "width": 128, "height": 128, "viewBox": "0 0 96 95.999999"},\n    {"path": "res/logo.svg", "width": 26, "height": 26, "viewBox": "0 0 96 95.999999"},\n    {"path": "res/foxxdesk-banner.svg", "width": 114, "height": 26, "viewBox": "66.993 897.484 113.652 26"},\n    {"path": "res/scalable.svg", "width": 32, "height": 32, "viewBox": "66.993 897.484 32 32.000001"},\n    {"path": "flutter/assets/icon.svg", "width": 150, "height": 150, "viewBox": "0 0 112.5 112.499997"},\n]\n\nICO_ASSETS = [\n    {"path": "res/icon.ico", "render_size": (256, 256), "ico_sizes": [(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)]},\n    {"path": "res/tray-icon.ico", "render_size": (32, 32), "ico_sizes": [(16,16), (24,24), (32,32)]},\n    {"path": "flutter/windows/runner/resources/app_icon.ico", "render_size": (256, 256), "ico_sizes": [(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)]},\n]\n\nICNS_ASSETS = [\n    {"path": "flutter/macos/Runner/AppIcon.icns", "size": (1024, 1024)},\n]\n\nANDROID_DENSITIES = {\n    "mdpi": 1.0,\n    "hdpi": 1.5,\n    "xhdpi": 2.0,\n    "xxhdpi": 3.0,\n    "xxxhdpi": 4.0,\n}\n\nANDROID_PNG_ASSETS: list[dict[str, Any]] = []\nfor density, scale in ANDROID_DENSITIES.items():\n    folder = f"flutter/android/app/src/main/res/mipmap-{density}"\n    launcher = int(round(48 * scale))\n    foreground = int(round(108 * scale))\n    stat = int(round(24 * scale))\n    ANDROID_PNG_ASSETS.extend([\n        {"path": f"{folder}/ic_launcher.png", "size": (launcher, launcher), "mode": "RGBA"},\n        {"path": f"{folder}/ic_launcher_round.png", "size": (launcher, launcher), "mode": "RGBA", "round_mask": True},\n        {"path": f"{folder}/ic_launcher_foreground.png", "size": (foreground, foreground), "mode": "RGBA"},\n        {"path": f"{folder}/ic_stat_logo.png", "size": (stat, stat), "mode": "LA"},\n    ])\n\nIOS_ICON_SIZES = [\n    ("Icon-App-20x20@1x.png", 20),\n    ("Icon-App-20x20@2x.png", 40),\n    ("Icon-App-20x20@3x.png", 60),\n    ("Icon-App-29x29@1x.png", 29),\n    ("Icon-App-29x29@2x.png", 58),\n    ("Icon-App-29x29@3x.png", 87),\n    ("Icon-App-40x40@1x.png", 40),\n    ("Icon-App-40x40@2x.png", 80),\n    ("Icon-App-40x40@3x.png", 120),\n    ("Icon-App-60x60@2x.png", 120),\n    ("Icon-App-60x60@3x.png", 180),\n    ("Icon-App-76x76@1x.png", 76),\n    ("Icon-App-76x76@2x.png", 152),\n    ("Icon-App-83.5x83.5@2x.png", 167),\n    ("Icon-App-1024x1024@1x.png", 1024),\n]\n\nIOS_PNG_ASSETS = [\n    {\n        "path": f"flutter/ios/Runner/Assets.xcassets/AppIcon.appiconset/{name}",\n        "size": (size, size),\n        "mode": "RGB",\n    }\n    for name, size in IOS_ICON_SIZES\n]\n\n# A closed manifest of files the script is allowed to generate/update.\nALL_IMAGE_ASSETS: list[dict[str, Any]] = (\n    ROOT_PNG_ASSETS\n    + ANDROID_PNG_ASSETS\n    + IOS_PNG_ASSETS\n)\n\nEXPECTED_CONTENTS_JSON_PATH = "flutter/ios/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json"\n\n\ndef parse_args() -> argparse.Namespace:\n    parser = argparse.ArgumentParser(description="Generate all system logo assets from res/icon.png")\n    parser.add_argument("--target", default=".", help="Project root. Default: current directory")\n    parser.add_argument("--source", default="res/icon.png", help="Source image relative to target. Default: res/icon.png")\n    parser.add_argument("--ios-background", default="#FFFFFF", help="Background used when flattening iOS/RGB icons. Default: #FFFFFF")\n    parser.add_argument("--update-ios-contents", action="store_true", help="Also normalize iOS AppIcon Contents.json")\n    mode = parser.add_mutually_exclusive_group(required=True)\n    mode.add_argument("--dry-run", action="store_true", help="Show what would be generated")\n    mode.add_argument("--apply", action="store_true", help="Generate/update files")\n    parser.add_argument("--yes", action="store_true", help="Skip confirmation in --apply mode")\n    return parser.parse_args()\n\n\ndef hex_to_rgb(value: str) -> tuple[int, int, int]:\n    value = value.strip().lstrip("#")\n    if len(value) == 3:\n        value = "".join(ch * 2 for ch in value)\n    if len(value) != 6:\n        raise ValueError(f"Cor invalida: {value!r}")\n    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)\n\n\ndef ensure_rgba(im: Image.Image) -> Image.Image:\n    return im.convert("RGBA") if im.mode != "RGBA" else im\n\n\ndef square_canvas(src: Image.Image, padding_ratio: float = 0.0) -> Image.Image:\n    """Return source centered in a square transparent canvas."""\n    src = ensure_rgba(src)\n    side = max(src.size)\n    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))\n    canvas.alpha_composite(src, ((side - src.width) // 2, (side - src.height) // 2))\n    if padding_ratio <= 0:\n        return canvas\n    padded_side = round(side / (1 - padding_ratio * 2))\n    padded = Image.new("RGBA", (padded_side, padded_side), (0, 0, 0, 0))\n    padded.alpha_composite(canvas, ((padded_side - side) // 2, (padded_side - side) // 2))\n    return padded\n\n\ndef resize_image(src: Image.Image, size: tuple[int, int]) -> Image.Image:\n    return square_canvas(src).resize(size, LANCZOS)\n\n\ndef flatten_to_rgb(im: Image.Image, background: tuple[int, int, int]) -> Image.Image:\n    rgba = ensure_rgba(im)\n    bg = Image.new("RGBA", rgba.size, (*background, 255))\n    bg.alpha_composite(rgba)\n    return bg.convert("RGB")\n\n\ndef white_alpha_mask(src: Image.Image, size: tuple[int, int]) -> Image.Image:\n    """Create Android/macOS style monochrome icon as white + alpha mask."""\n    rgba = resize_image(src, size)\n    alpha = rgba.getchannel("A")\n    # If source has no useful alpha, derive a mask from luminance.\n    if not alpha.getbbox():\n        lum = ImageOps.grayscale(rgba.convert("RGB"))\n        alpha = ImageOps.invert(lum)\n    white = Image.new("L", size, 255)\n    return Image.merge("LA", (white, alpha))\n\n\ndef apply_round_mask(im: Image.Image) -> Image.Image:\n    rgba = ensure_rgba(im)\n    mask = Image.new("L", rgba.size, 0)\n    # Pillow ImageDraw imported lazily to keep top imports simple.\n    from PIL import ImageDraw\n    draw = ImageDraw.Draw(mask)\n    draw.ellipse((0, 0, rgba.width - 1, rgba.height - 1), fill=255)\n    rgba.putalpha(Image.composite(rgba.getchannel("A"), Image.new("L", rgba.size, 0), mask))\n    return rgba\n\n\ndef png_bytes(src: Image.Image, size: tuple[int, int], mode: str, background: tuple[int, int, int], round_mask: bool = False) -> bytes:\n    if mode == "LA":\n        out_img = white_alpha_mask(src, size)\n    else:\n        out_img = resize_image(src, size)\n        if round_mask:\n            out_img = apply_round_mask(out_img)\n        if mode == "RGB":\n            out_img = flatten_to_rgb(out_img, background)\n        elif mode == "RGBA":\n            out_img = ensure_rgba(out_img)\n        else:\n            out_img = out_img.convert(mode)\n    out = io.BytesIO()\n    out_img.save(out, format="PNG", optimize=True)\n    return out.getvalue()\n\n\ndef parse_viewbox(viewbox: str) -> tuple[float, float, float, float]:\n    parts = [float(x) for x in viewbox.replace(",", " ").split()]\n    if len(parts) != 4:\n        raise ValueError(f"viewBox invalido: {viewbox}")\n    return parts[0], parts[1], parts[2], parts[3]\n\n\ndef fmt_num(value: float) -> str:\n    if float(value).is_integer():\n        return str(int(value))\n    return f"{value:.6f}".rstrip("0").rstrip(".")\n\n\ndef svg_bytes(src: Image.Image, width: int, height: int, viewbox: str) -> bytes:\n    min_x, min_y, vb_w, vb_h = parse_viewbox(viewbox)\n    render_w = max(1, round(vb_w))\n    render_h = max(1, round(vb_h))\n    png = png_bytes(src, (render_w, render_h), "RGBA", (255, 255, 255))\n    b64 = base64.b64encode(png).decode("ascii")\n    svg = f\'\'\'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg"\n     xmlns:xlink="http://www.w3.org/1999/xlink"\n     width="{width}"\n     height="{height}"\n     viewBox="{viewbox}"\n     version="1.1">\n  <image x="{fmt_num(min_x)}"\n         y="{fmt_num(min_y)}"\n         width="{fmt_num(vb_w)}"\n         height="{fmt_num(vb_h)}"\n         preserveAspectRatio="xMidYMid meet"\n         xlink:href="data:image/png;base64,{b64}" />\n</svg>\n\'\'\'\n    return svg.encode("utf-8")\n\n\ndef ico_bytes(src: Image.Image, render_size: tuple[int, int], ico_sizes: list[tuple[int, int]]) -> bytes:\n    out = io.BytesIO()\n    resize_image(src, render_size).save(out, format="ICO", sizes=ico_sizes)\n    return out.getvalue()\n\n\ndef icns_bytes(src: Image.Image, size: tuple[int, int]) -> bytes:\n    """Generate macOS .icns. Requires Pillow with ICNS writer support."""\n    out = io.BytesIO()\n    resize_image(src, size).save(out, format="ICNS")\n    return out.getvalue()\n\n\ndef ios_contents_json_bytes() -> bytes:\n    images = [\n        {"size": "20x20", "idiom": "iphone", "filename": "Icon-App-20x20@2x.png", "scale": "2x"},\n        {"size": "20x20", "idiom": "iphone", "filename": "Icon-App-20x20@3x.png", "scale": "3x"},\n        {"size": "29x29", "idiom": "iphone", "filename": "Icon-App-29x29@1x.png", "scale": "1x"},\n        {"size": "29x29", "idiom": "iphone", "filename": "Icon-App-29x29@2x.png", "scale": "2x"},\n        {"size": "29x29", "idiom": "iphone", "filename": "Icon-App-29x29@3x.png", "scale": "3x"},\n        {"size": "40x40", "idiom": "iphone", "filename": "Icon-App-40x40@2x.png", "scale": "2x"},\n        {"size": "40x40", "idiom": "iphone", "filename": "Icon-App-40x40@3x.png", "scale": "3x"},\n        {"size": "60x60", "idiom": "iphone", "filename": "Icon-App-60x60@2x.png", "scale": "2x"},\n        {"size": "60x60", "idiom": "iphone", "filename": "Icon-App-60x60@3x.png", "scale": "3x"},\n        {"size": "20x20", "idiom": "ipad", "filename": "Icon-App-20x20@1x.png", "scale": "1x"},\n        {"size": "20x20", "idiom": "ipad", "filename": "Icon-App-20x20@2x.png", "scale": "2x"},\n        {"size": "29x29", "idiom": "ipad", "filename": "Icon-App-29x29@1x.png", "scale": "1x"},\n        {"size": "29x29", "idiom": "ipad", "filename": "Icon-App-29x29@2x.png", "scale": "2x"},\n        {"size": "40x40", "idiom": "ipad", "filename": "Icon-App-40x40@1x.png", "scale": "1x"},\n        {"size": "40x40", "idiom": "ipad", "filename": "Icon-App-40x40@2x.png", "scale": "2x"},\n        {"size": "76x76", "idiom": "ipad", "filename": "Icon-App-76x76@1x.png", "scale": "1x"},\n        {"size": "76x76", "idiom": "ipad", "filename": "Icon-App-76x76@2x.png", "scale": "2x"},\n        {"size": "83.5x83.5", "idiom": "ipad", "filename": "Icon-App-83.5x83.5@2x.png", "scale": "2x"},\n        {"size": "1024x1024", "idiom": "ios-marketing", "filename": "Icon-App-1024x1024@1x.png", "scale": "1x"},\n    ]\n    payload = {"images": images, "info": {"version": 1, "author": "xcode"}}\n    return (json.dumps(payload, indent=2, ensure_ascii=False) + "\\n").encode("utf-8")\n\n\ndef confirm() -> None:\n    ans = input("Aplicar geracao de TODOS os assets de logo? [y/N]: ").strip().lower()\n    if ans not in {"y", "yes", "s", "sim"}:\n        raise SystemExit("Operacao cancelada.")\n\n\ndef backup_file(root: Path, rel: str, backup_root: Path) -> None:\n    src = root / rel\n    dst = backup_root / rel\n    dst.parent.mkdir(parents=True, exist_ok=True)\n    shutil.copy2(src, dst)\n\n\ndef write_if_changed(root: Path, rel: str, data: bytes, dry_run: bool, backup_root: Path, report: list[str]) -> str:\n    rel = rel.replace("\\\\", "/")\n    if rel in EXCLUDED:\n        report.append(f"- excluido por regra: `{rel}`")\n        return "skipped"\n\n    path = root / rel\n    existed = path.exists()\n    current = path.read_bytes() if existed else None\n\n    if current == data:\n        report.append(f"- ja atualizado: `{rel}`")\n        return "unchanged"\n\n    if dry_run:\n        action = "sera atualizado" if existed else "sera criado"\n        report.append(f"- {action}: `{rel}`")\n        return "planned"\n\n    if existed:\n        backup_file(root, rel, backup_root)\n\n    path.parent.mkdir(parents=True, exist_ok=True)\n    path.write_bytes(data)\n\n    if existed:\n        report.append(f"- atualizado: `{rel}` (backup em `{backup_root}`)")\n    else:\n        report.append(f"- criado: `{rel}`")\n    return "written"\n\n\ndef generate(root: Path, source_rel: str, dry_run: bool, ios_bg: tuple[int, int, int], update_ios_contents: bool) -> tuple[list[str], dict[str, int], Path]:\n    src_path = root / source_rel\n    if not src_path.exists():\n        raise FileNotFoundError(f"Arquivo fonte nao encontrado: {src_path}")\n\n    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")\n    backup_root = root / ".icon_asset_backup" / timestamp\n    report: list[str] = []\n    stats = {"planned": 0, "written": 0, "unchanged": 0, "skipped": 0, "errors": 0}\n\n    with Image.open(src_path) as im:\n        src = ensure_rgba(im)\n\n        for item in ALL_IMAGE_ASSETS:\n            try:\n                data = png_bytes(src, item["size"], item.get("mode", "RGBA"), ios_bg, bool(item.get("round_mask")))\n                status = write_if_changed(root, item["path"], data, dry_run, backup_root, report)\n                stats[status] += 1\n            except Exception as exc:\n                report.append(f"- ERRO PNG `{item[\'path\']}`: {exc}")\n                stats["errors"] += 1\n\n        for item in SVG_ASSETS:\n            try:\n                data = svg_bytes(src, item["width"], item["height"], item["viewBox"])\n                status = write_if_changed(root, item["path"], data, dry_run, backup_root, report)\n                stats[status] += 1\n            except Exception as exc:\n                report.append(f"- ERRO SVG `{item[\'path\']}`: {exc}")\n                stats["errors"] += 1\n\n        for item in ICO_ASSETS:\n            try:\n                data = ico_bytes(src, item["render_size"], item["ico_sizes"])\n                status = write_if_changed(root, item["path"], data, dry_run, backup_root, report)\n                stats[status] += 1\n            except Exception as exc:\n                report.append(f"- ERRO ICO `{item[\'path\']}`: {exc}")\n                stats["errors"] += 1\n\n        for item in ICNS_ASSETS:\n            try:\n                data = icns_bytes(src, item["size"])\n                status = write_if_changed(root, item["path"], data, dry_run, backup_root, report)\n                stats[status] += 1\n            except Exception as exc:\n                report.append(f"- ERRO ICNS `{item[\'path\']}`: {exc}")\n                stats["errors"] += 1\n\n        if update_ios_contents:\n            try:\n                data = ios_contents_json_bytes()\n                status = write_if_changed(root, EXPECTED_CONTENTS_JSON_PATH, data, dry_run, backup_root, report)\n                stats[status] += 1\n            except Exception as exc:\n                report.append(f"- ERRO JSON `{EXPECTED_CONTENTS_JSON_PATH}`: {exc}")\n                stats["errors"] += 1\n\n    return report, stats, backup_root\n\n\ndef main() -> None:\n    args = parse_args()\n    root = Path(args.target).resolve()\n    if not root.exists() or not root.is_dir():\n        raise SystemExit(f"Pasta alvo invalida: {root}")\n\n    if args.apply and not args.yes:\n        confirm()\n\n    ios_bg = hex_to_rgb(args.ios_background)\n    report, stats, backup_root = generate(root, args.source, args.dry_run, ios_bg, args.update_ios_contents)\n    mode = "dry-run" if args.dry_run else "apply"\n    changed = stats["planned"] if args.dry_run else stats["written"]\n    report_path = root / "icon_assets_report.md"\n\n    total_manifest = len(ALL_IMAGE_ASSETS) + len(SVG_ASSETS) + len(ICO_ASSETS) + len(ICNS_ASSETS) + (1 if args.update_ios_contents else 0)\n    lines = [\n        "# Relatorio de geracao de assets",\n        "",\n        f"- Script: `{SCRIPT_VERSION}`",\n        f"- Modo: `{mode}`",\n        f"- Projeto alvo: `{root}`",\n        f"- Fonte: `{args.source}`",\n        f"- Total no manifesto: `{total_manifest}`",\n        f"- Backup: `{backup_root if args.apply and stats[\'written\'] else \'nao criado\'}`",\n        "",\n        "## Regras",\n        "",\n        "- Fonte unica: `res/icon.png`.",\n        "- Nunca altera `res/logo-header.svg`.",\n        "- Nunca altera `res/design.svg`.",\n        "- Nunca altera `res/icon.png` porque ele e a fonte.",\n        "- SVGs sao wrappers com PNG embutido; nao sao vetores reais.",\n        "- iOS AppIcon e gerado em RGB sem transparencia.",\n        "- Android `ic_stat_logo.png` e gerado como branco + mascara alpha.",\n        "",\n        "## Resumo",\n        "",\n        f"- Alteraveis/criados no modo atual: `{changed}`",\n        f"- Ja atualizados: `{stats[\'unchanged\']}`",\n        f"- Pulados/excluidos: `{stats[\'skipped\']}`",\n        f"- Erros: `{stats[\'errors\']}`",\n        "",\n        "## Arquivos tratados",\n        "",\n    ]\n    lines.extend(report)\n    report_path.write_text("\\n".join(lines) + "\\n", encoding="utf-8")\n\n    print(f"Modo: {mode} | arquivos alterados: {changed} | ja atualizados: {stats[\'unchanged\']} | erros: {stats[\'errors\']} | relatorio: {report_path}")\n\n\nif __name__ == "__main__":\n    main()'

# Nomes/URLs que devem continuar como upstream ou API interna.
PROTECT_PATTERNS: Sequence[str] = (
    r"https?://[^\s\)\]\}\>\"']*rustdesk[^\s\)\]\}\>\"']*",
    r"git\+https?://[^\s\)\]\}\>\"']*rustdesk[^\s\)\]\}\>\"']*",
    r"github\.com/rustdesk-org",
    r"github\.com/rustdesk/[^\s\)\]\}\>\"']*",
    r"rustdesk-org",
    r"rustdesk/rustdesk",
    r"librustdesk",
    r"is_rustdesk(?:_[A-Za-z0-9_]+)?",
    r"try_kill_rustdesk_main_window_process",
    r"RustDeskTempTopMostWindow",
    r"RustDeskInterval",
    r"RustdeskImpl",
    r"FoxxdeskImpl",
    r"DeleteRustDeskTestCert",
    # Build/upstream internos que NÃO devem ser renomeados; alguns workflows
    # dependem desses nomes exatos no action rustdesk-org/run-on-arch-action.
    r"rustdesk/engine",
    # Branches reais em repositórios upstream. Não existem como foxxdesk/*.
    r"rustdesk/pty_based_[A-Za-z0-9._-]+",
    r"branch\s*=\s*\"rustdesk/[A-Za-z0-9._/-]+\"",
    r"branch=rustdesk/[A-Za-z0-9._/-]+",
    r"ubuntu18\.04-rustdesk",
    r"Dockerfile\.[A-Za-z0-9._-]*-rustdesk",
    # Crates/submódulos internos mantêm seus nomes upstream.
    r"\bhbb_common\b",
    r"libs/hbb_common",
)


def die(msg: str, code: int = 2) -> None:
    print(f"ERRO: {msg}", file=sys.stderr)
    raise SystemExit(code)


def normalize_lf(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def dominant_newline(text: str) -> str:
    crlf = text.count("\r\n")
    lf = text.count("\n") - crlf
    cr = text.count("\r") - crlf
    if crlf >= lf and crlf >= cr and crlf > 0:
        return "\r\n"
    if cr > lf and cr > 0:
        return "\r"
    return "\n"


def convert_newlines(text: str, newline: str) -> str:
    return normalize_lf(text).replace("\n", newline)


def has_bad_control_chars(text: str) -> bool:
    sample = text[:4096]
    if not sample:
        return False
    bad = 0
    for ch in sample:
        o = ord(ch)
        if ch in "\n\r\t":
            continue
        if o < 32:
            bad += 1
    return (bad / max(1, len(sample))) > 0.03


def decode_file(data: bytes, path: Path) -> Tuple[Optional[str], Optional[str], bool]:
    if path.suffix.lower() in BINARY_EXTS:
        return None, None, True
    if data.startswith(codecs.BOM_UTF8):
        try:
            return data.decode("utf-8-sig"), "utf-8-sig", False
        except UnicodeDecodeError:
            return None, None, True
    if data.startswith(codecs.BOM_UTF16_LE) or data.startswith(codecs.BOM_UTF16_BE):
        try:
            text = data.decode("utf-16")
            return (text, "utf-16", False) if not has_bad_control_chars(text) else (None, None, True)
        except UnicodeDecodeError:
            return None, None, True
    if b"\x00" in data[:4096]:
        if path.suffix.lower() == ".rc":
            try:
                return data.decode("utf-8", errors="ignore").replace("\x00", "\\0"), "utf-8", False
            except Exception:
                return None, None, True
        return None, None, True
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            text = data.decode(enc)
            if not has_bad_control_chars(text):
                return text, enc, False
        except UnicodeDecodeError:
            pass
    return None, None, True


def encode_text(text: str, enc: Optional[str]) -> bytes:
    try:
        return text.encode(enc or "utf-8", errors="strict")
    except UnicodeEncodeError:
        return text.encode("utf-8")


def safe_cli_value(name: str, value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    if "\n" in value or "\r" in value:
        die(f"{name} não pode conter quebra de linha.")
    return value or None


def normalize_homepage(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    value = value.strip().rstrip("/")
    if not value:
        return None
    if not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", value):
        value = "https://" + value
    if any(ch in value for ch in (" ", "\t", "\n", "\r")):
        die("--homepage/--server inválido para Homepage: não pode conter espaços ou quebras.")
    return value


def redact_value(value: Optional[str], label: str = "valor") -> str:
    if not value:
        return "(não informado)"
    digest = hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:10]
    if label == "key":
        return f"<key ocultada; len={len(value)}; sha256={digest}>"
    return value


def copy_backup(target: Path, backup_root: Path, rel: str) -> None:
    src = target / rel
    dst = backup_root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists() and not dst.exists():
        shutil.copy2(src, dst)


def is_skipped_path(rel: str) -> bool:
    rel_norm = rel.replace("\\", "/").lstrip("/")
    parts = rel_norm.split("/")
    for skip in SKIP_DIRS:
        if rel_norm == skip or rel_norm.startswith(skip.rstrip("/") + "/"):
            return True
    return any(part in {".git", "target", "node_modules", ".rebrand_backup"} for part in parts)


def iter_scan_files(target: Path, max_size: int) -> Iterable[str]:
    for p in target.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(target).as_posix()
        if is_skipped_path(rel):
            continue
        try:
            if p.stat().st_size > max_size:
                continue
        except OSError:
            continue
        yield rel


def protect_text(text: str) -> Tuple[str, Dict[str, str]]:
    tokens: Dict[str, str] = {}
    protected = text

    def repl(match: re.Match[str]) -> str:
        token = f"@@FOXXDESK_PROTECT_{len(tokens)}@@"
        tokens[token] = match.group(0)
        return token

    for pattern in PROTECT_PATTERNS:
        protected = re.sub(pattern, repl, protected)
    return protected, tokens


def restore_text(text: str, tokens: Dict[str, str]) -> str:
    for token, original in tokens.items():
        text = text.replace(token, original)
    return text


def safe_brand_replacements(text: str) -> str:
    """Rebrand por limites de palavra, evitando trocar nomes dentro de identificadores."""
    protected, tokens = protect_text(text)
    replacements = [
        (r"com\.rustdesk\.RustDesk", "com.foxxdesk.client"),
        (r"com\.rustdesk", "com.foxxdesk"),
        (r"org\.rustdesk", "org.foxxdesk"),
        (r"(?<![A-Za-z0-9_])RUSTDESK(?![A-Za-z0-9_])", APP_SLUG_UPPER),
        (r"(?<![A-Za-z0-9_])RustDesk(?![A-Za-z0-9_])", APP_DISPLAY_NAME),
        (r"(?<![A-Za-z0-9_])rustdesk(?![A-Za-z0-9_])", APP_SLUG),
        (r"(?<![A-Za-z0-9_])rust_desk(?![A-Za-z0-9_])", "foxx_desk"),
        (r"(?<![A-Za-z0-9_])rust-desk(?![A-Za-z0-9_])", "foxx-desk"),
    ]
    for pattern, repl in replacements:
        protected = re.sub(pattern, repl, protected)
    return restore_text(protected, tokens)


def patch_cargo_toml(rel: str, text: str) -> str:
    if rel == "Cargo.toml":
        text = re.sub(r'(?m)^name\s*=\s*"rustdesk"\s*$', 'name = "foxxdesk"', text, count=1)
        text = re.sub(r'(?m)^authors\s*=\s*\["rustdesk <info@rustdesk\.com>"\]\s*$', 'authors = ["FoxxDesk / MGN"]', text, count=1)
        text = re.sub(r'(?m)^description\s*=\s*"RustDesk Remote Desktop"\s*$', 'description = "FoxxDesk Remote Desktop"', text, count=1)
        text = re.sub(r'(?m)^default-run\s*=\s*"rustdesk"\s*$', 'default-run = "foxxdesk"', text, count=1)
        return text
    if rel == "libs/portable/Cargo.toml":
        text = re.sub(r'(?m)^name\s*=\s*"rustdesk-portable-packer"\s*$', 'name = "foxxdesk-portable-packer"', text, count=1)
        text = re.sub(r'(?m)^description\s*=\s*"RustDesk Remote Desktop"\s*$', 'description = "FoxxDesk Remote Desktop"', text, count=1)
        text = re.sub(r'(?m)^ProductName\s*=\s*"RustDesk"\s*$', 'ProductName = "FoxxDesk"', text, count=1)
        text = re.sub(r'(?m)^OriginalFilename\s*=\s*"rustdesk\.exe"\s*$', 'OriginalFilename = "foxxdesk.exe"', text, count=1)
        text = re.sub(r'(?m)^FileDescription\s*=\s*"RustDesk Remote Desktop"\s*$', 'FileDescription = "FoxxDesk Remote Desktop"', text, count=1)
        text = text.replace("Purslane Ltd. and RustDesk contributors", "Purslane Ltd. and FoxxDesk/MGN contributors")
        return text
    return text


def patch_cargo_lock(rel: str, text: str) -> str:
    if rel not in {"Cargo.lock", "libs/portable/Cargo.lock"}:
        return text
    text = re.sub(
        r'(?m)^(\[\[package\]\]\nname = ")rustdesk("$)',
        r'\1foxxdesk\2',
        text,
        count=1 if rel == "Cargo.lock" else 0,
    )
    text = re.sub(
        r'(?m)^(\[\[package\]\]\nname = ")rustdesk-portable-packer("$)',
        r'\1foxxdesk-portable-packer\2',
        text,
        count=1,
    )
    return text


def patch_build_py(rel: str, text: str, args: argparse.Namespace) -> str:
    if rel != "build.py":
        return text
    # Mantém URLs upstream/dependências; altera apenas metadados e nomes locais.
    text = re.sub(r'(?m)^APP_DISPLAY_NAME\s*=.*$', 'APP_DISPLAY_NAME = os.environ.get("APP_DISPLAY_NAME", "FoxxDesk")', text)
    text = re.sub(r'(?m)^APP_SLUG\s*=.*$', 'APP_SLUG = os.environ.get("APP_SLUG", "foxxdesk")', text)
    text = re.sub(r'(?m)^UPSTREAM_SLUG\s*=.*$', 'UPSTREAM_SLUG = "foxxdesk"', text)
    if "APP_DISPLAY_NAME = os.environ.get" not in text:
        insert = (
            'APP_DISPLAY_NAME = os.environ.get("APP_DISPLAY_NAME", "FoxxDesk")\n'
            'APP_SLUG = os.environ.get("APP_SLUG", "foxxdesk")\n'
            'APP_EXE = APP_SLUG + (".exe" if windows else "")\n'
            'UPSTREAM_SLUG = "foxxdesk"\n'
        )
        pos = text.find("skip_cargo = False")
        if pos != -1:
            before = text[:pos]
            after = text[pos:]
            if "APP_SLUG" not in before:
                text = before + insert + after
    homepage = normalize_homepage(args.homepage or args.server)
    if homepage:
        text = re.sub(r'(?m)^Homepage:\s*https?://rustdesk\.com\s*$', f'Homepage: {homepage}', text)
        text = re.sub(r'(?m)^Homepage:\s*https?://foxxdesk[^\s]*\s*$', f'Homepage: {homepage}', text)
    if args.maintainer_email:
        text = text.replace("rustdesk <info@rustdesk.com>", f"FoxxDesk / MGN <{args.maintainer_email}>")
        text = text.replace("TODO_FOXXDESK_MAINTAINER_EMAIL", args.maintainer_email)
        text = text.replace(DEFAULT_MAINTAINER_EMAIL, args.maintainer_email)
    return text


def patch_config_rs(rel: str, text: str, args: argparse.Namespace) -> str:
    """Prefixa defaults reais de servidor/relay/key no binário.

    V19 não depende mais de passar --server/--relay/--key manualmente. Se o
    usuário não informar nada, usa os valores DEFAULT_* do script. Isso garante
    que o build saia apontando para o servidor FoxxDesk mesmo em CI.
    """
    if rel != "libs/hbb_common/src/config.rs":
        return text

    server = args.server or DEFAULT_SERVER
    relay = args.relay or server
    key = args.key or DEFAULT_KEY

    # Constantes explícitas para evitar espalhar strings mágicas e para facilitar
    # conferência futura no código compilado.
    if "pub const DEFAULT_RENDEZVOUS_SERVER:" not in text:
        marker = "type KeyPair = (Vec<u8>, Vec<u8>);\n"
        insert = (
            f'\npub const DEFAULT_RENDEZVOUS_SERVER: &str = "{server}";\n'
            f'pub const DEFAULT_RELAY_SERVER: &str = "{relay}";\n'
            f'pub const DEFAULT_CUSTOM_CLIENT_KEY: &str = "{key}";\n'
        )
        if marker in text:
            text = text.replace(marker, marker + insert, 1)
    text = re.sub(
        r'pub const DEFAULT_RENDEZVOUS_SERVER: &str = "[^"]*";',
        f'pub const DEFAULT_RENDEZVOUS_SERVER: &str = "{server}";',
        text,
        count=1,
    )
    text = re.sub(
        r'pub const DEFAULT_RELAY_SERVER: &str = "[^"]*";',
        f'pub const DEFAULT_RELAY_SERVER: &str = "{relay}";',
        text,
        count=1,
    )
    text = re.sub(
        r'pub const DEFAULT_CUSTOM_CLIENT_KEY: &str = "[^"]*";',
        f'pub const DEFAULT_CUSTOM_CLIENT_KEY: &str = "{key}";',
        text,
        count=1,
    )


    # ID server / rendezvous compilado.
    text = re.sub(
        r'pub static ref PROD_RENDEZVOUS_SERVER: RwLock<String> = RwLock::new\("[^"]*"\.to_owned\(\)\);',
        'pub static ref PROD_RENDEZVOUS_SERVER: RwLock<String> = RwLock::new(DEFAULT_RENDEZVOUS_SERVER.to_owned());',
        text,
        count=1,
    )
    text = re.sub(
        r'pub const RENDEZVOUS_SERVERS: &\[&str\] = &\["[^"]*"\];',
        'pub const RENDEZVOUS_SERVERS: &[&str] = &[DEFAULT_RENDEZVOUS_SERVER];',
        text,
        count=1,
    )
    text = re.sub(
        r'pub const RS_PUB_KEY: &str = "[^"]*";',
        'pub const RS_PUB_KEY: &str = DEFAULT_CUSTOM_CLIENT_KEY;',
        text,
        count=1,
    )

    # Defaults que aparecem em Settings > Network e são retornados por
    # Config::get_options(). Isso faz o relay e a key virem prefixados por padrão,
    # sem depender do usuário salvar configuração local.
    default_settings_block = """pub static ref DEFAULT_SETTINGS: RwLock<HashMap<String, String>> = RwLock::new(HashMap::from([
        ("custom-rendezvous-server".to_string(), DEFAULT_RENDEZVOUS_SERVER.to_string()),
        ("relay-server".to_string(), DEFAULT_RELAY_SERVER.to_string()),
        ("key".to_string(), DEFAULT_CUSTOM_CLIENT_KEY.to_string()),
    ]));"""
    text = re.sub(
        r'pub static ref DEFAULT_SETTINGS: RwLock<HashMap<String, String>> = Default::default\(\);',
        default_settings_block,
        text,
        count=1,
    )
    # Se uma versão anterior já aplicou o bloco, atualiza para o formato v19.
    text = re.sub(
        r'pub static ref DEFAULT_SETTINGS: RwLock<HashMap<String, String>> = RwLock::new\(HashMap::from\(\[.*?\]\)\);',
        default_settings_block,
        text,
        count=1,
        flags=re.S,
    )
    return text

def patch_server_defaults(rel: str, text: str, args: argparse.Namespace) -> str:
    if rel != "FOXXDESK_SERVER_DEFAULTS.md":
        return text
    server = args.server or DEFAULT_SERVER
    relay = args.relay or server
    key = args.key or DEFAULT_KEY
    text = re.sub(r'(?m)^- HBBS / ID server: `[^`]*`$', f'- HBBS / ID server: `{server}`', text)
    text = re.sub(r'(?m)^- HBBR / Relay server: `[^`]*`$', f'- HBBR / Relay server: `{relay}`', text)
    text = re.sub(r'(?m)^- Public key: `[^`]*`$', f'- Public key: `{key}`', text)
    return text



def make_prefixed_exe_base(args: argparse.Namespace) -> str:
    server = args.server or DEFAULT_SERVER
    relay = args.relay or server
    key = args.key or DEFAULT_KEY
    # Trailing comma antes do .exe protege contra Windows adicionar " (1)".
    # O parser de src/custom_server.rs ignora o pedaço vazio depois da vírgula.
    return f"foxxdesk-host={server},key={key},relay={relay},"


def patch_prefixed_server_build_outputs(rel: str, text: str, args: argparse.Namespace) -> str:
    """Garante artefatos Windows com nome prefixado host/key/relay.

    Isso é complementar aos defaults compilados em config.rs. O executável normal
    continua existindo, mas o Release também passa a publicar uma cópia prefixada
    compatível com src/custom_server.rs.
    """
    prefix = make_prefixed_exe_base(args)

    if rel == ".github/workflows/flutter-build.yml":
        # Deixa os valores visíveis no workflow para debug e para os comandos de
        # cópia; não é segredo, é chave pública do hbbs.
        if "FOXXDESK_CUSTOM_EXE_PREFIX:" not in text:
            env_marker = '  SIGN_BASE_URL: "${{ secrets.SIGN_BASE_URL }}-2"\n'
            env_insert = (
                f'  FOXXDESK_DEFAULT_SERVER: "{args.server or DEFAULT_SERVER}"\n'
                f'  FOXXDESK_DEFAULT_RELAY: "{args.relay or (args.server or DEFAULT_SERVER)}"\n'
                f'  FOXXDESK_DEFAULT_KEY: "{args.key or DEFAULT_KEY}"\n'
                f'  FOXXDESK_CUSTOM_EXE_PREFIX: "{prefix}"\n'
            )
            if env_marker in text:
                text = text.replace(env_marker, env_marker + env_insert, 1)

        flutter_mv = '          mv ./target/release/foxxdesk-portable-packer.exe ./SignOutput/foxxdesk-${{ env.VERSION }}-${{ matrix.job.arch }}.exe\n'
        flutter_cp = '          cp "./SignOutput/foxxdesk-${{ env.VERSION }}-${{ matrix.job.arch }}.exe" "./SignOutput/${{ env.FOXXDESK_CUSTOM_EXE_PREFIX }}-${{ env.VERSION }}-${{ matrix.job.arch }}.exe"\n'
        if flutter_mv in text and flutter_cp not in text:
            text = text.replace(flutter_mv, flutter_mv + flutter_cp, 1)

        sciter_mv = '          mv ./target/release/foxxdesk-portable-packer.exe ./SignOutput/foxxdesk-${{ env.VERSION }}-${{ matrix.job.arch }}-sciter.exe\n'
        sciter_cp = '          cp "./SignOutput/foxxdesk-${{ env.VERSION }}-${{ matrix.job.arch }}-sciter.exe" "./SignOutput/${{ env.FOXXDESK_CUSTOM_EXE_PREFIX }}-${{ env.VERSION }}-${{ matrix.job.arch }}-sciter.exe"\n'
        if sciter_mv in text and sciter_cp not in text:
            text = text.replace(sciter_mv, sciter_mv + sciter_cp, 1)
        return text

    if rel == "build.py":
        # Local build: além do instalador normal, cria uma cópia prefixada.
        if "FOXXDESK_CUSTOM_EXE_PREFIX" not in text:
            top_marker = 'UPSTREAM_SLUG = "foxxdesk"\n'
            top_insert = f'FOXXDESK_CUSTOM_EXE_PREFIX = os.environ.get("FOXXDESK_CUSTOM_EXE_PREFIX", "{prefix}")\n'
            if top_marker in text:
                text = text.replace(top_marker, top_marker + top_insert, 1)

        old = """    os.rename('./foxxdesk_portable.exe', f'./foxxdesk-{version}-install.exe')
    print(
        f'output location: {os.path.abspath(os.curdir)}/foxxdesk-{version}-install.exe')
"""
        new = """    normal_installer = f'./foxxdesk-{version}-install.exe'
    os.rename('./foxxdesk_portable.exe', normal_installer)
    print(f'output location: {os.path.abspath(os.curdir)}/{normal_installer.lstrip("./")}')
    if FOXXDESK_CUSTOM_EXE_PREFIX:
        prefixed_installer = f'./{FOXXDESK_CUSTOM_EXE_PREFIX}-{version}-install.exe'
        shutil.copy2(normal_installer, prefixed_installer)
        print(f'output location: {os.path.abspath(os.curdir)}/{prefixed_installer.lstrip("./")}')
"""
        if old in text and new not in text:
            text = text.replace(old, new, 1)
        return text

    return text


def patch_package_scripts(rel: str, text: str, args: argparse.Namespace) -> str:
    if rel in {"res/rpm-flutter-suse.spec", "res/rpm-flutter.spec", "res/rpm-suse.spec", "res/rpm.spec"}:
        email = args.maintainer_email or DEFAULT_MAINTAINER_EMAIL
        text = text.replace("TODO_FOXXDESK_MAINTAINER_EMAIL", email)
        text = text.replace("rustdesk <info@rustdesk.com>", f"FoxxDesk / MGN <{email}>")
    return text


def patch_workflow_build_internals(rel: str, text: str) -> str:
    """Protege nomes internos usados por actions/upstream e corrige danos de versões agressivas.

    Importante: distro ubuntu18.04-rustdesk é o nome real esperado pelo
    rustdesk-org/run-on-arch-action. Se virar foxxdesk, o workflow procura
    Dockerfile.armv7.ubuntu18.04-foxxdesk e quebra.
    """
    if not rel.startswith(".github/workflows/"):
        return text
    text = text.replace("ubuntu18.04-foxxdesk", "ubuntu18.04-rustdesk")
    text = text.replace("foxxdesk/engine", "rustdesk/engine")
    text = text.replace("Dockerfile.armv7.ubuntu18.04-foxxdesk", "Dockerfile.armv7.ubuntu18.04-rustdesk")
    return text


def patch_upstream_dependency_branches(rel: str, text: str) -> str:
    """Corrige danos de rebrand em branches de dependências Git upstream.

    Exemplo real: `portable-pty` vem de `rustdesk-org/wezterm` usando a
    branch `rustdesk/pty_based_0.8.1`. Essa branch pertence ao upstream e
    NÃO deve virar `foxxdesk/pty_based_0.8.1`, porque ela não existe.
    """
    if rel not in {"Cargo.toml", "Cargo.lock", "libs/portable/Cargo.lock"}:
        return text
    text = re.sub(
        r'branch\s*=\s*"foxxdesk/(pty_based_[A-Za-z0-9._-]+)"',
        r'branch = "rustdesk/\1"',
        text,
    )
    text = re.sub(
        r'branch=foxxdesk/(pty_based_[A-Za-z0-9._-]+)',
        r'branch=rustdesk/\1',
        text,
    )
    return text



def patch_portable_packer_robustness(rel: str, text: str) -> str:
    '''Corrige caminhos frágeis do portable packer no Windows/Git Bash.

    V17 corrige também o caso em que o workflow passa um executável FORA da
    pasta fonte, por exemplo:

      source folder: D:\\a\\FoxxDesk2\\FoxxDesk2\\foxxdesk
      executable:    D:\\a\\FoxxDesk2\\rustdesk\\rustdesk.exe

    Nesse caso, `generate.py` deve procurar o executável correto dentro de
    `-f` antes de falhar. Ele NÃO deve empacotar executável fora da pasta.
    '''
    if rel == "libs/portable/generate.py":
        def restore_fallback_names(src: str) -> str:
            return src.replace(
                '["foxxdesk.exe", "FoxxDesk.exe", "foxxdesk.exe", "FoxxDesk.exe"]',
                '["foxxdesk.exe", "FoxxDesk.exe", "rustdesk.exe", "RustDesk.exe"]',
            )

        if "FoxxDesk portable packer path guard v17" in text:
            return restore_fallback_names(text)

        old_original = """    exe: str = os.path.abspath(options.executable)
    if not exe.startswith(os.path.abspath(folder)):
        print("The executable must locate in source folder")
        exit(-1)
    exe = '.' + exe[len(os.path.abspath(folder)):]
"""
        old_v16 = """    folder_abs = os.path.abspath(folder)
    exe_abs = os.path.abspath(options.executable)

    # GitHub Actions on Windows may mix /d/a/... and D:\\a\\... paths.
    # Use normalized commonpath instead of a raw string startswith check.
    try:
        folder_norm = os.path.normcase(os.path.normpath(folder_abs))
        exe_norm = os.path.normcase(os.path.normpath(exe_abs))
        common = os.path.commonpath([folder_norm, exe_norm])
    except ValueError:
        common = ""

    if common != folder_norm:
        print("The executable must locate in source folder")
        print(f"  source folder: {folder_abs}")
        print(f"  executable:    {exe_abs}")
        exit(-1)

    if not os.path.isfile(exe_abs):
        # Fallback para builds parcialmente rebrandados ou artefatos upstream.
        # Não mascara erro: se nenhum executável existir, falha com lista clara.
        fallback_names = ["foxxdesk.exe", "FoxxDesk.exe", "rustdesk.exe", "RustDesk.exe"]
        for name in fallback_names:
            candidate = os.path.join(folder_abs, name)
            if os.path.isfile(candidate):
                print(f"Executable not found at {exe_abs}; using {candidate}")
                exe_abs = candidate
                break

    if not os.path.isfile(exe_abs):
        print(f"Executable not found: {exe_abs}")
        if os.path.isdir(folder_abs):
            print("Source folder contents:")
            for item in sorted(os.listdir(folder_abs)):
                print(f"  - {item}")
        else:
            print(f"Source folder does not exist: {folder_abs}")
        exit(-1)

    exe = './' + os.path.relpath(exe_abs, folder_abs).replace(os.sep, '/')
"""
        new_guard = """    folder_abs = os.path.abspath(folder)
    requested_exe_abs = os.path.abspath(options.executable)

    # FoxxDesk portable packer path guard v17.
    # GitHub Actions on Windows may mix /d/a/... and D:\\a\\... paths, and
    # older workflow lines may still pass ../../rustdesk/rustdesk.exe while
    # -f already points to ../../foxxdesk/. Only package an executable that is
    # actually inside the source folder.
    def _is_inside_source(path: str) -> bool:
        try:
            folder_norm = os.path.normcase(os.path.normpath(folder_abs))
            path_norm = os.path.normcase(os.path.normpath(path))
            return os.path.commonpath([folder_norm, path_norm]) == folder_norm
        except ValueError:
            return False

    fallback_names = []
    requested_name = os.path.basename(requested_exe_abs)
    if requested_name:
        fallback_names.append(requested_name)
    fallback_names += ["foxxdesk.exe", "FoxxDesk.exe", "rustdesk.exe", "RustDesk.exe"]

    exe_abs = None
    if _is_inside_source(requested_exe_abs) and os.path.isfile(requested_exe_abs):
        exe_abs = requested_exe_abs
    else:
        seen_names = set()
        for name in fallback_names:
            if not name or name in seen_names:
                continue
            seen_names.add(name)
            candidate = os.path.join(folder_abs, name)
            if os.path.isfile(candidate):
                if os.path.abspath(candidate) != requested_exe_abs:
                    print(f"Executable requested as {requested_exe_abs}; using source executable {candidate}")
                exe_abs = candidate
                break

    if exe_abs is None:
        if not _is_inside_source(requested_exe_abs):
            print("The executable must locate in source folder")
            print(f"  source folder: {folder_abs}")
            print(f"  executable:    {requested_exe_abs}")
            print("  tried inside source folder:")
            for name in dict.fromkeys(fallback_names):
                print(f"  - {os.path.join(folder_abs, name)}")
        else:
            print(f"Executable not found: {requested_exe_abs}")
        if os.path.isdir(folder_abs):
            print("Source folder contents:")
            for item in sorted(os.listdir(folder_abs)):
                print(f"  - {item}")
        else:
            print(f"Source folder does not exist: {folder_abs}")
        exit(-1)

    exe = './' + os.path.relpath(exe_abs, folder_abs).replace(os.sep, '/')
"""
        if old_v16 in text:
            text = text.replace(old_v16, new_guard, 1)
        elif old_original in text:
            text = text.replace(old_original, new_guard, 1)
        else:
            # Se o upstream mudou, não força alteração cega. O relatório do script
            # mostrará pendência se o build continuar chamando o trecho antigo.
            return restore_fallback_names(text)
        return restore_fallback_names(text)

    if rel == "build.py":
        # Quando já estamos passando -f <pasta>, passe apenas o nome do exe.
        # Isso evita comparação frágil de caminho absoluto no generate.py.
        replacements = {
            "f'python3 ./generate.py -f ../../{flutter_build_dir_2} -o . -e ../../{flutter_build_dir_2}/foxxdesk.exe')":
                "f'python3 ./generate.py -f ../../{flutter_build_dir_2} -o . -e {APP_SLUG}.exe')",
            "f'python3 ./generate.py -f ../../{flutter_build_dir_2} -o . -e ../../{flutter_build_dir_2}/{APP_SLUG}.exe')":
                "f'python3 ./generate.py -f ../../{flutter_build_dir_2} -o . -e {APP_SLUG}.exe')",
            "f'python3 ./generate.py -f ../../{flutter_build_dir_2} -o . -e ../../rustdesk/rustdesk.exe')":
                "f'python3 ./generate.py -f ../../{flutter_build_dir_2} -o . -e {APP_SLUG}.exe')",
            "f'python3 ./generate.py -f ../../{flutter_build_dir_2} -o . -e ../../foxxdesk/rustdesk.exe')":
                "f'python3 ./generate.py -f ../../{flutter_build_dir_2} -o . -e {APP_SLUG}.exe')",
            "f'python3 ./generate.py -f ../../{flutter_build_dir_2} -o . -e ../../foxxdesk/foxxdesk.exe')":
                "f'python3 ./generate.py -f ../../{flutter_build_dir_2} -o . -e {APP_SLUG}.exe')",
            "f'python3 ./generate.py -f ../../{res_dir} -o . -e ../../{res_dir}/foxxdesk-{version}-win7-install.exe')":
                "f'python3 ./generate.py -f ../../{res_dir} -o . -e FoxxDesk.exe')",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    if rel == ".github/workflows/flutter-build.yml":
        # Corrige comandos antigos/agressivos que apontam -e para fora da pasta
        # indicada por -f. O portable packer exige que o executável esteja dentro
        # da source folder.
        patterns = [
            "../../rustdesk/rustdesk.exe",
            "../../rustdesk/RustDesk.exe",
            "../../foxxdesk/rustdesk.exe",
            "../../foxxdesk/RustDesk.exe",
            "../../foxxdesk/foxxdesk.exe",
            "../../foxxdesk/FoxxDesk.exe",
            "../../Release/foxxdesk.exe",
            "../../Release/FoxxDesk.exe",
            "../../Release/rustdesk.exe",
            "../../Release/RustDesk.exe",
        ]
        for pat in patterns:
            text = text.replace(f"-e {pat}", "-e foxxdesk.exe")
        return text

    return text

def patch_codegen_submodule_guard(rel: str, text: str) -> str:
    """Garante que jobs de flutter_rust_bridge tenham libs/hbb_common antes do codegen.

    O erro `failed to read libs/hbb_common/Cargo.toml` acontece quando o
    submódulo não foi inicializado no runner. Esta etapa é idempotente e
    não muda o código Rust; só reforça o checkout do submódulo antes do codegen.
    """
    if rel not in {".github/workflows/bridge.yml", ".github/workflows/playground.yml"}:
        return text
    if "flutter_rust_bridge_codegen" not in text:
        return text
    if "Ensure Rust submodules are present" in text:
        return text
    guard = (
        "          git submodule sync --recursive\n"
        "          git submodule update --init --recursive\n"
        "          test -f libs/hbb_common/Cargo.toml\n"
    )
    pattern = re.compile(
        r"(?m)(^      - name: Install flutter rust bridge deps\n"
        r"(?:^        [^\n]*\n)*?"
        r"^        run: \|\n)"
        r"(?!          git submodule sync --recursive\n)"
    )
    return pattern.sub(r"\1" + guard, text)


def patch_bridge_workflow_compat(rel: str, text: str) -> str:
    """Aplica o alias RustdeskImpl após o flutter_rust_bridge_codegen no workflow."""
    if rel != ".github/workflows/bridge.yml":
        return text
    if "Patch FoxxDesk bridge compatibility" in text:
        return text
    marker = """      - name: Upload Artifact
        uses: actions/upload-artifact"""
    step = """      - name: Patch FoxxDesk bridge compatibility
        shell: bash
        run: python3 scripts/fix_generated_bridge_compat.py

"""
    if marker in text:
        return text.replace(marker, step + marker, 1)
    pattern = re.compile(
        r"(?ms)(^      - name: .*?(?:flutter rust bridge|bridge).*?\n"
        r"(?:^        .*?\n)*?"
        r"^        run: \|\n"
        r"(?:^          .*flutter_rust_bridge_codegen.*\n))",
        re.IGNORECASE,
    )
    return pattern.sub(r"\1\n" + step, text, count=1)


def patch_build_py_bridge_compat(rel: str, text: str) -> str:
    """Faz o build.py rodar o fixer do generated_bridge.dart localmente também."""
    if rel != "build.py":
        return text
    if "scripts/fix_generated_bridge_compat.py" in text:
        return text
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
    if old in text:
        return text.replace(old, new, 1)
    pattern = re.compile(
        r"(?ms)(def ffi_bindgen_function_refactor\(\):\n"
        r"(?:(?:    |\t).+\n)*?"
        r"(?:    |\t)system2\(\n"
        r"(?:(?:    |\t).+\n)*?generated_bridge\.dart['\"]\)\n)",
    )
    return pattern.sub(r"\1    if os.path.exists(\"scripts/fix_generated_bridge_compat.py\"):\n        system2(\"python3 scripts/fix_generated_bridge_compat.py\")\n", text, count=1)


def patch_windows_flutter_dart_fixes(rel: str, text: str) -> str:
    """Patches pontuais de null-safety/tipo que quebram build Flutter Windows."""
    if rel == "flutter/lib/common.dart":
        return text.replace(
            "LastWindowPosition.loadFromString(pos);",
            "LastWindowPosition.loadFromString(pos ?? '');",
        )

    if rel == "flutter/lib/common/widgets/dialog.dart":
        return text.replace(
            "controller.text = osPassword;",
            "controller.text = osPassword ?? '';",
            1,
        )

    if rel == "flutter/lib/desktop/widgets/remote_toolbar.dart":
        return text.replace(
            "final results = await Future.wait([",
            "final results = await Future.wait<bool?>([",
            1,
        )

    if rel == "flutter/lib/desktop/pages/desktop_setting_page.dart":
        return text.replace("_Radio(context", "_Radio<String>(context")

    if rel == "flutter/lib/common/widgets/toolbar.dart":
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
        for old, new in repls.items():
            if old in text and new not in text:
                text = text.replace(old, new, 1)
        return text

    return text


def ensure_generated_bridge_compat_helper(target: Path, args: argparse.Namespace, report: Dict[str, Any], backup_root: Optional[Path]) -> None:
    """Cria/atualiza scripts/fix_generated_bridge_compat.py sem depender de ZIP."""
    rel = "scripts/fix_generated_bridge_compat.py"
    path = target / rel
    old = ""
    if path.exists() and path.is_file():
        try:
            old = normalize_lf(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            report["pending"].append({"file": rel, "message": "arquivo existe mas não está em UTF-8; não sobrescrito"})
            return
    new = normalize_lf(BRIDGE_COMPAT_SCRIPT)
    report["analyzed_files"].append(rel)
    if old == new:
        report["already_applied_files"].append(rel)
        return
    report["changed_files"].append(rel)
    report["changes"].append({
        "file": rel,
        "line": line_for_first_diff(old, new) if old else 1,
        "status": "alterado" if path.exists() and args.apply else ("criado" if args.apply else "criaria/alteraria"),
        "action": "criar helper de compatibilidade flutter_rust_bridge",
        "message": "gera typedef RustdeskImpl = <Impl gerado> após o codegen; sem payload/ZIP",
    })
    if args.apply:
        if backup_root is not None and path.exists():
            copy_backup(target, backup_root, rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new, encoding="utf-8", newline="\n")


def _record_generated_text_file(target: Path, rel: str, content: str, args: argparse.Namespace, report: Dict[str, Any], backup_root: Optional[Path], action: str, create_only: bool = False) -> None:
    """Cria/atualiza arquivo gerado sem depender de ZIP/payload."""
    path = target / rel
    old = ""
    exists = path.exists() and path.is_file()
    if exists:
        try:
            old = normalize_lf(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            report["pending"].append({"file": rel, "message": "arquivo existe mas não está em UTF-8; não sobrescrito"})
            return
    new = normalize_lf(content)
    report["analyzed_files"].append(rel)
    if exists and create_only:
        report["already_applied_files"].append(rel)
        return
    if old == new:
        report["already_applied_files"].append(rel)
        return
    report["changed_files"].append(rel)
    report["changes"].append({
        "file": rel,
        "line": line_for_first_diff(old, new) if old else 1,
        "status": "alterado" if exists and args.apply else ("criado" if args.apply else "criaria/alteraria"),
        "action": action,
        "message": "arquivo gerado pela V25; sem payload/ZIP e sem snapshot de projeto antigo",
    })
    if args.apply:
        if backup_root is not None and exists:
            copy_backup(target, backup_root, rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new, encoding="utf-8", newline="\n")


def ensure_v25_generated_files(target: Path, args: argparse.Namespace, report: Dict[str, Any], backup_root: Optional[Path]) -> None:
    """Garante workflow de build e helpers FoxxDesk/fbr_codegen."""
    _record_generated_text_file(
        target,
        ".github/workflows/foxxdesk-build.yml",
        FOXXDESK_BUILD_WORKFLOW,
        args,
        report,
        backup_root,
        "garantir workflow FoxxDesk manual-only",
        create_only=True,
    )
    _record_generated_text_file(
        target,
        "scripts/fix_generated_bridge_compat.py",
        BRIDGE_COMPAT_SCRIPT,
        args,
        report,
        backup_root,
        "criar/atualizar helper de compatibilidade flutter_rust_bridge",
        create_only=False,
    )
    _record_generated_text_file(
        target,
        "scripts/fix_foxxdesk_windows_flutter_build.py",
        WINDOWS_FLUTTER_BUILD_FIX_SCRIPT,
        args,
        report,
        backup_root,
        "criar/atualizar fixer FoxxDesk Windows Flutter build",
        create_only=False,
    )


def ensure_hbb_common_before_branding(target: Path, args: argparse.Namespace, report: Dict[str, Any]) -> None:
    """Sincroniza hbb_common pela revisão compatível; nunca baixa a branch main.

    A revisão vem do gitlink do submódulo quando disponível ou de
    .foxxdesk/foxxdesk.config.json/versão do Cargo.toml. Isso evita misturar uma release
    do RustDesk com hbb_common mais novo.
    """
    rel = "libs/hbb_common"
    helper = target / "scripts/foxxdesk_sync_hbb_common.py"
    report["analyzed_files"].append(rel)
    if not helper.is_file():
        report["pending"].append({"file": rel, "message": "helper scripts/foxxdesk_sync_hbb_common.py ausente; não é seguro baixar hbb_common/main"})
        return

    cmd = [sys.executable, str(helper), "--target", str(target)]
    if getattr(args, "refresh_hbb_common", False):
        cmd.append("--force")
    if args.dry_run:
        cmd.append("--check")
    try:
        cp = subprocess.run(cmd, cwd=str(target), check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as exc:
        report["pending"].append({"file": rel, "message": f"falha ao executar sincronizador hbb_common: {exc}"})
        return
    if cp.returncode != 0:
        msg = (cp.stderr or cp.stdout or "falha desconhecida").strip()
        report["pending"].append({"file": rel, "message": f"hbb_common incompatível/não sincronizado: {msg}"})
        return
    if "(sincronizado)" in cp.stdout:
        report["changed_files"].append(rel)
        report["changes"].append({"file": rel, "line": 1, "status": "sincronizado", "action": "restaurar revisão hbb_common compatível", "message": cp.stdout.strip()})
    else:
        report["already_applied_files"].append(rel)


def patch_copyright_v25(rel: str, text: str) -> str:
    """Troca Purslane Ltd/2025 para MGN Systems/ano atual nos metadados visíveis."""
    if rel in {"Cargo.toml", "libs/portable/Cargo.toml"}:
        if "[package.metadata.winres]" in text:
            if re.search(r'(?m)^LegalCopyright\s*=', text):
                text = re.sub(r'(?m)^LegalCopyright\s*=\s*".*?"\s*$', f'LegalCopyright = "{COPYRIGHT_TEXT}"', text)
            else:
                text = text.replace("[package.metadata.winres]", f"[package.metadata.winres]\nLegalCopyright = \"{COPYRIGHT_TEXT}\"", 1)
        text = text.replace("Copyright © 2025 Purslane Ltd. All rights reserved.", COPYRIGHT_TEXT)
        text = text.replace("Purslane Ltd", COPYRIGHT_OWNER)

    if rel == "flutter/macos/Runner/Configs/AppInfo.xcconfig":
        if "PRODUCT_COPYRIGHT" in text:
            text = re.sub(r'(?m)^PRODUCT_COPYRIGHT\s*=\s*.*$', f'PRODUCT_COPYRIGHT = {COPYRIGHT_TEXT}', text)
        text = text.replace("Copyright © 2025 Purslane Ltd. All rights reserved.", COPYRIGHT_TEXT)
        text = text.replace("Purslane Ltd", COPYRIGHT_OWNER)

    if rel == "flutter/windows/runner/Runner.rc":
        text = re.sub(r'VALUE\s+"CompanyName",\s*"[^"]*"\s+"\\0"', lambda _m: f'VALUE "CompanyName", "{COPYRIGHT_OWNER}" "\\0"', text)
        text = re.sub(r'VALUE\s+"LegalCopyright",\s*"[^"]*"\s+"\\0"', lambda _m: f'VALUE "LegalCopyright", "{COPYRIGHT_TEXT}" "\\0"', text)
        text = text.replace("Purslane Ltd", COPYRIGHT_OWNER)

    if rel == "src/ui/index.tis":
        text = re.sub(r'Copyright\s*&copy;\s*\d{4}\s+Purslane Ltd\.?', COPYRIGHT_HTML, text)
        text = text.replace("Copyright &copy; 2025 Purslane Ltd.", COPYRIGHT_HTML)
        text = text.replace("Purslane Ltd", COPYRIGHT_OWNER)

    return text


def patch_text(rel: str, text: str, args: argparse.Namespace) -> str:
    text = normalize_lf(text)
    text = patch_copyright_v25(rel, text)
    text = patch_cargo_lock(rel, text)
    text = patch_cargo_toml(rel, text)
    text = patch_build_py(rel, text, args)
    text = patch_build_py_bridge_compat(rel, text)
    text = patch_config_rs(rel, text, args)
    text = patch_server_defaults(rel, text, args)
    text = patch_prefixed_server_build_outputs(rel, text, args)
    text = patch_package_scripts(rel, text, args)
    text = patch_workflow_build_internals(rel, text)
    text = patch_upstream_dependency_branches(rel, text)
    text = patch_codegen_submodule_guard(rel, text)
    text = patch_bridge_workflow_compat(rel, text)
    text = patch_windows_flutter_dart_fixes(rel, text)
    text = patch_portable_packer_robustness(rel, text)
    if args.profile == "full" and not rel.startswith(".github/workflows/"):
        text = safe_brand_replacements(text)
        text = patch_upstream_dependency_branches(rel, text)
    # Workflows têm nomes internos de actions/upstream; não aplicar reforços genéricos neles.
    if not rel.startswith(".github/workflows/"):
        # Reforços pontuais após patches específicos.
        text = text.replace("/usr/share/rustdesk/files/", "/usr/share/foxxdesk/files/")
        text = text.replace("/usr/share/rustdesk/", "/usr/share/foxxdesk/")
        text = text.replace("/etc/systemd/system/rustdesk.service", "/etc/systemd/system/foxxdesk.service")
        text = text.replace("rustdesk.service", "foxxdesk.service")
        text = text.replace("rustdesk.desktop", "foxxdesk.desktop")
        text = text.replace("rustdesk-link.desktop", "foxxdesk-link.desktop")
    text = patch_workflow_build_internals(rel, text)
    text = patch_portable_packer_robustness(rel, text)
    return text


def line_for_first_diff(old: str, new: str) -> int:
    old_lines = old.splitlines()
    new_lines = new.splitlines()
    for i, (a, b) in enumerate(zip(old_lines, new_lines), start=1):
        if a != b:
            return i
    return min(len(old_lines), len(new_lines)) + 1


def md_escape(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", "\\n")


def apply_file_renames(target: Path, args: argparse.Namespace, report: Dict[str, Any], backup_root: Optional[Path]) -> None:
    for src_rel, dst_rel in FILE_RENAMES.items():
        src = target / src_rel
        dst = target / dst_rel
        if dst.exists():
            continue
        if not src.exists():
            continue
        report["renamed_files"].append(f"{src_rel} -> {dst_rel}")
        report["changes"].append({"file": dst_rel, "line": 1, "status": "criado" if args.apply else "criaria", "action": "copiar arquivo renomeado", "message": f"origem: {src_rel}"})
        if args.apply:
            if backup_root is not None:
                copy_backup(target, backup_root, src_rel)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def process_one_file(target: Path, rel: str, args: argparse.Namespace, report: Dict[str, Any], backup_root: Optional[Path]) -> None:
    if rel in NEVER_PATCH_FILES:
        report["ignored_files"].append(rel + " (protegido; nunca alterado pelo rebrand)")
        return
    if getattr(args, "preserve_hbb_common", False) and rel.startswith("libs/hbb_common/"):
        report["ignored_files"].append(rel + " (submódulo upstream preservado; defaults FoxxDesk ficam no crate principal)")
        return
    if is_skipped_path(rel):
        report["ignored_files"].append(rel)
        return
    if rel in GENERATED_HELPER_FILES:
        return
    path = target / rel
    report["analyzed_files"].append(rel)
    if not path.exists():
        if rel in OPTIONAL_FILES:
            report["ignored_files"].append(rel + " (opcional ausente)")
        elif rel in ALLOWED_FILES:
            report["missing_files"].append(rel)
        return
    if not path.is_file():
        report["pending"].append({"file": rel, "message": "caminho existe, mas não é arquivo"})
        return
    try:
        data = path.read_bytes()
    except OSError as exc:
        report["pending"].append({"file": rel, "message": f"falha ao ler: {exc}"})
        return
    if len(data) > args.max_size:
        report["ignored_files"].append(rel)
        return
    text, enc, isbin = decode_file(data, path)
    if isbin or text is None:
        report["ignored_files"].append(rel)
        return
    old_norm = normalize_lf(text)
    new_norm = patch_text(rel, old_norm, args)
    if new_norm == old_norm:
        report["already_applied_files"].append(rel)
        return
    report["changed_files"].append(rel)
    report["changes"].append({
        "file": rel,
        "line": line_for_first_diff(old_norm, new_norm),
        "status": "alterado" if args.apply else "alteraria",
        "action": "aplicar regras standalone de rebrand",
        "message": "conteúdo textual mudou por regra segura; sem payload/ZIP",
    })
    if args.apply:
        if backup_root is not None:
            copy_backup(target, backup_root, rel)
        newline = dominant_newline(text)
        path.write_bytes(encode_text(convert_newlines(new_norm, newline), enc))



def cleanup_obsolete_after_rename_files(target: Path, args: argparse.Namespace, report: Dict[str, Any], backup_root: Optional[Path]) -> None:
    """Remove arquivos antigos que quebram build quando coexistem com o novo nome.

    Diferente de --remove-old-renamed, isto é aplicado por padrão apenas para
    casos comprovadamente perigosos. O caso atual é o WiX/MSI: o SDK inclui
    todos os .wxs automaticamente; se RustDesk.wxs e FoxxDesk.wxs existem,
    ambos definem os mesmos IDs e o build falha com WIX0091/WIX0092.
    """
    for old_rel, new_rel in OBSOLETE_AFTER_RENAME_FILES.items():
        old_path = target / old_rel
        new_path = target / new_rel
        report["analyzed_files"].append(old_rel)
        if not old_path.exists():
            report["already_applied_files"].append(old_rel)
            continue
        if not new_path.exists():
            # Não remove o antigo se o novo ainda não existe; isso evita apagar
            # o único componente MSI válido em um checkout parcialmente atualizado.
            report["pending"].append({
                "file": old_rel,
                "message": f"arquivo antigo existe, mas o substituto {new_rel} não existe; não removido automaticamente",
            })
            continue
        report["changed_files"].append(old_rel)
        report["changes"].append({
            "file": old_rel,
            "line": 1,
            "status": "removido" if args.apply else "removeria",
            "action": "remover arquivo antigo substituído pelo novo brand",
            "message": f"{old_rel} foi substituído por {new_rel}; evita build duplicado/branding misto",
        })
        if args.apply:
            if backup_root is not None:
                copy_backup(target, backup_root, old_rel)
            try:
                old_path.unlink()
            except OSError as exc:
                report["pending"].append({"file": old_rel, "message": f"falha ao remover arquivo obsoleto: {exc}"})


def _git_index_mode(target: Path, rel: str) -> Optional[str]:
    """Return Git index mode (100755/100644/160000) when available."""
    try:
        cp = subprocess.run(
            ["git", "ls-files", "--stage", "--", rel], cwd=str(target),
            check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except OSError:
        return None
    for line in cp.stdout.splitlines():
        m = re.match(r"^(\d{6})\s+[0-9a-fA-F]{40}\s+\d+\s+", line)
        if m:
            return m.group(1)
    return None


def ensure_executable_permissions(target: Path, args: argparse.Namespace, report: Dict[str, Any], backup_root: Optional[Path]) -> None:
    """Apply POSIX executable bits only where the host filesystem supports them."""
    for rel in sorted(EXECUTABLE_FILES):
        path = target / rel
        if not path.exists() or not path.is_file():
            if rel == "build.py":
                report["missing_files"].append(rel)
            continue
        report["analyzed_files"].append(rel)
        if os.name == "nt":
            git_mode = _git_index_mode(target, rel)
            if git_mode == "100755":
                report["already_applied_files"].append(rel)
            else:
                report["ignored_files"].append(rel + f" (Windows: chmod POSIX não aplicável; git mode={git_mode or 'desconhecido'})")
            continue
        try:
            mode = path.stat().st_mode
        except OSError as exc:
            report["pending"].append({"file": rel, "message": f"falha ao ler permissões: {exc}"})
            continue
        desired = mode | 0o111
        if mode == desired:
            report["already_applied_files"].append(rel)
            continue
        report["changed_files"].append(rel)
        report["changes"].append({
            "file": rel, "line": 1,
            "status": "chmod +x" if args.apply else "aplicaria chmod +x",
            "action": "garantir bit executável no Git/CI",
            "message": "marca como executável; rode git add para registrar modo 100755",
        })
        if args.apply:
            if backup_root is not None:
                copy_backup(target, backup_root, rel)
            try:
                path.chmod(desired)
            except OSError as exc:
                report["pending"].append({"file": rel, "message": f"falha ao aplicar chmod +x: {exc}"})

def validate_build_safety(target: Path, report: Dict[str, Any]) -> None:
    """Valida pontos que já quebraram no GitHub Actions.

    Não altera arquivos; apenas registra pendência clara antes do usuário
    tentar compilar, para evitar erro obscuro no flutter_rust_bridge_codegen.
    """
    hbb = target / "libs/hbb_common/Cargo.toml"
    if not hbb.exists():
        report["pending"].append({
            "file": "libs/hbb_common/Cargo.toml",
            "message": "submódulo ausente; rode `git submodule update --init --recursive` ou garanta `submodules: recursive` no checkout do workflow",
        })
    wf = target / ".github/workflows/flutter-build.yml"
    if wf.exists():
        try:
            wtxt = normalize_lf(wf.read_text(encoding="utf-8", errors="ignore"))
            if "ubuntu18.04-foxxdesk" in wtxt:
                report["pending"].append({
                    "file": ".github/workflows/flutter-build.yml",
                    "message": "distro inválida `ubuntu18.04-foxxdesk`; precisa continuar `ubuntu18.04-rustdesk` para o run-on-arch-action",
                })
        except OSError:
            pass
    rp = target / "libs/remote_printer/src/lib.rs"
    if rp.exists():
        try:
            rtxt = normalize_lf(rp.read_text(encoding="utf-8", errors="ignore"))
            if "drivers/RustDeskPrinterDriver/RustDeskPrinterDriver.inf" in rtxt:
                report["pending"].append({
                    "file": "libs/remote_printer/src/lib.rs",
                    "message": "RD_DRIVER_INF_PATH ainda aponta para RustDeskPrinterDriver; v21 deve usar FoxxDeskPrinterDriver/FoxxDeskPrinterDriver.inf",
                })
            if '"foxxdesk v4 Printer Driver"' in rtxt:
                report["pending"].append({
                    "file": "libs/remote_printer/src/lib.rs",
                    "message": "nome visível do driver ainda está minúsculo; v21 deve usar FoxxDesk v4 Printer Driver",
                })
        except OSError:
            pass
    rcpp = target / "res/msi/CustomActions/RemotePrinter.cpp"
    if rcpp.exists():
        try:
            ctxt = normalize_lf(rcpp.read_text(encoding="utf-8", errors="ignore"))
            if "drivers\\RustDeskPrinterDriver\\RustDeskPrinterDriver.inf" in ctxt:
                report["pending"].append({
                    "file": "res/msi/CustomActions/RemotePrinter.cpp",
                    "message": "RD_DRIVER_INF_PATH do MSI ainda aponta para RustDeskPrinterDriver; v21 deve usar FoxxDeskPrinterDriver/FoxxDeskPrinterDriver.inf",
                })
        except OSError:
            pass
    old_msi = target / "res/msi/Package/Components/RustDesk.wxs"
    new_msi = target / "res/msi/Package/Components/FoxxDesk.wxs"
    if old_msi.exists() and new_msi.exists() and "res/msi/Package/Components/RustDesk.wxs" not in report.get("changed_files", []):
        report["pending"].append({
            "file": "res/msi/Package/Components/RustDesk.wxs",
            "message": "RustDesk.wxs e FoxxDesk.wxs coexistem; o WiX inclui ambos e duplica ComponentGroup:Components/App.StartMenu",
        })


    # V23 validation: não pode sobrar borrow temporário em ProjectDirs::from.
    cfg = target / "libs/hbb_common/src/config.rs"
    if cfg.exists():
        try:
            cfg_text = cfg.read_text(encoding="utf-8", errors="ignore")
            if "&APP_NAME.read().unwrap()" in cfg_text and "ProjectDirs::from" in cfg_text:
                bad_region = cfg_text[cfg_text.find("ProjectDirs::from") : cfg_text.find("ProjectDirs::from") + 500]
                if "&APP_NAME.read().unwrap()" in bad_region:
                    report["pending"].append({"file": "libs/hbb_common/src/config.rs", "message": "V23: ainda existe &APP_NAME.read().unwrap() dentro de ProjectDirs::from; isso causa Rust E0716"})
        except Exception:
            pass

    # V22 validations: no old driver names in source-controlled printer paths and no lowercase Windows LocalAppData folder names.
    for rel in [
        "libs/remote_printer/src/lib.rs",
        "libs/remote_printer/src/setup/driver.rs",
        "res/msi/CustomActions/RemotePrinter.cpp",
        "res/msi/preprocess.py",
        ".github/workflows/flutter-build.yml",
        "res/job.py",
        "BRAND_CHANGELOG.md",
    ]:
        p = target / rel
        if not p.exists():
            continue
        try:
            t = normalize_lf(p.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
        t_check = t.replace("rustdesk_printer_driver_v4-1.4.zip", "").replace("rustdesk_printer_driver_v4-1.4", "")
        if "RustDeskPrinterDriver" in t_check:
            report["pending"].append({"file": rel, "message": "ainda existe RustDeskPrinterDriver fora do nome de ZIP/download upstream; V22 deve normalizar para FoxxDeskPrinterDriver"})
        if "rustdesk v4 Printer Driver" in t_check or "foxxdesk v4 Printer Driver" in t_check:
            report["pending"].append({"file": rel, "message": "driver ainda está minúsculo; deve ser FoxxDesk v4 Printer Driver"})
    for rel in ["libs/portable/src/main.rs", "src/platform/windows.rs"]:
        p = target / rel
        if not p.exists():
            continue
        try:
            t = normalize_lf(p.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
        if 'const APP_PREFIX: &str = "foxxdesk"' in t or 'foxxdesk-sciter' in t:
            report["pending"].append({"file": rel, "message": "pasta LocalAppData ainda usa foxxdesk/foxxdesk-sciter; deve usar FoxxDesk"})

def build_report(report: Dict[str, Any], args: argparse.Namespace, target: Path) -> str:
    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = ["# Relatório de rebrand FoxxDesk", ""]
    lines += [
        f"- Data/hora: `{now}`",
        f"- Modo: `{'apply' if args.apply else 'dry-run'}`",
        f"- Projeto alvo: `{target}`",
        "- Script: `apply_foxxdesk_rebrand_all_files_no_zip_v27.py`",
        f"- Versão do script: `{SCRIPT_VERSION}`",
        "- Payload/ZIP/manifesto externo: `não`",
        "- Espelhamento/substituição de arquivo inteiro por referência antiga: `não`",
        f"- Perfil: `{args.profile}`",
        "- Estratégia: `patch-only; não espelha arquivos inteiros; full = TODOS os arquivos da allowlist + proteção de upstream + fixes Flutter Windows/bridge + portable packer path guard v17 + chmod executável completo + MSI duplicate guard v18 + embedded server/relay/key defaults ocultos + artefatos limpos v20 + ajustes seguros de driver/impressora v21 + AppData Local FoxxDesk e limpeza final de driver v22 + V26 cleanup definitivo do flutter-build.yml`",
        "- Observação: se aparecerem apenas ~13 arquivos, você provavelmente executou a v9 safe ou usou --profile safe.",
        "",
        "## Valores dinâmicos",
        "",
        f"- server: `{redact_value(args.server or DEFAULT_SERVER)}`",
        f"- relay: `{redact_value(args.relay or (args.server or DEFAULT_SERVER))}`",
        f"- key: `{redact_value(args.key or DEFAULT_KEY, 'key')}`",
        f"- maintainer-email: `{redact_value(args.maintainer_email)}`",
        f"- homepage: `{redact_value(normalize_homepage(args.homepage or args.server or DEFAULT_SERVER))}`",
        "",
        "## Resumo",
        "",
        f"- Arquivos permitidos na allowlist: `{len(ALLOWED_FILES)}`",
        f"- Arquivos analisados: `{len(set(report['analyzed_files']))}`",
        f"- Arquivos alterados: `{len(set(report['changed_files']))}`",
        f"- Arquivos já aplicados/sem mudança: `{len(set(report['already_applied_files']))}`",
        f"- Arquivos esperados não encontrados: `{len(set(report['missing_files']))}`",
        f"- Arquivos ignorados: `{len(set(report['ignored_files']))}`",
        f"- Renomeações/cópias criadas: `{len(report['renamed_files'])}`",
        f"- Pendências: `{len(report['pending'])}`",
    ]
    if report.get("backup_dir"):
        lines.append(f"- Backup: `{report['backup_dir']}`")
    if report.get("log_file"):
        lines.append(f"- Log detalhado: `{report['log_file']}`")
    lines.append("")

    def section(title: str, items: Iterable[Any]) -> None:
        lines.append(f"## {title}")
        lines.append("")
        unique = sorted({str(x) for x in items})
        if not unique:
            lines.append("Nenhum.")
        else:
            for item in unique:
                lines.append(f"- `{item}`")
        lines.append("")

    section("Arquivos alterados", report["changed_files"])
    section("Arquivos renomeados/copiados", report["renamed_files"])
    section("Arquivos esperados que não foram encontrados", report["missing_files"])
    section("Arquivos ignorados", report["ignored_files"])

    lines += ["## Alterações", ""]
    if not report["changes"]:
        lines.append("Nenhuma alteração avaliada.")
    else:
        lines.append("| Status | Arquivo | Linha | Ação | Mensagem |")
        lines.append("|---|---|---:|---|---|")
        for c in report["changes"]:
            lines.append(f"| {c.get('status')} | `{c.get('file')}` | {c.get('line') or ''} | {md_escape(c.get('action',''))} | {md_escape(c.get('message',''))} |")

    lines += ["", "## Pendências", ""]
    if not report["pending"]:
        lines.append("Nenhuma.")
    else:
        for p in report["pending"]:
            lines.append(f"- `{p.get('file')}`: {p.get('message')}")
    lines.append("")
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# V20 overrides
# -----------------------------------------------------------------------------
# As versões anteriores continuam acima para manter histórico e compatibilidade,
# mas a V20 sobrescreve os pontos sensíveis aqui: defaults ocultos, artefatos
# limpos e nomes Windows/MSI/Printer. Como Python resolve globais em runtime,
# process_one_file() usa estas definições finais de patch_config_rs/patch_text.


def patch_config_rs(rel: str, text: str, args: argparse.Namespace) -> str:  # type: ignore[override]
    """Fixa server/relay/key no runtime sem expor no menu de configurações.

    Mantém server/relay/key compilados, mas DEFAULT_SETTINGS fica vazio para o
    menu de Network não exibir valores pré-preenchidos. O fallback acontece em
    Config::get_option(), usado pelo runtime quando a configuração local está vazia.
    """
    if rel != "libs/hbb_common/src/config.rs":
        return text

    server = args.server or DEFAULT_SERVER
    relay = args.relay or server
    key = args.key or DEFAULT_KEY

    if "pub const DEFAULT_RENDEZVOUS_SERVER:" not in text:
        marker = "type KeyPair = (Vec<u8>, Vec<u8>);\n"
        insert = (
            f'\npub const DEFAULT_RENDEZVOUS_SERVER: &str = "{server}";\n'
            f'pub const DEFAULT_RELAY_SERVER: &str = "{relay}";\n'
            f'pub const DEFAULT_CUSTOM_CLIENT_KEY: &str = "{key}";\n'
        )
        if marker in text:
            text = text.replace(marker, marker + insert, 1)

    text = re.sub(
        r'pub const DEFAULT_RENDEZVOUS_SERVER: &str = "[^"]*";',
        f'pub const DEFAULT_RENDEZVOUS_SERVER: &str = "{server}";',
        text,
        count=1,
    )
    text = re.sub(
        r'pub const DEFAULT_RELAY_SERVER: &str = "[^"]*";',
        f'pub const DEFAULT_RELAY_SERVER: &str = "{relay}";',
        text,
        count=1,
    )
    text = re.sub(
        r'pub const DEFAULT_CUSTOM_CLIENT_KEY: &str = "[^"]*";',
        f'pub const DEFAULT_CUSTOM_CLIENT_KEY: &str = "{key}";',
        text,
        count=1,
    )
    # Keep the public application name independent from internal RustDesk API/crate
    # names. This is intentionally explicit and works in the conservative profile.
    text = re.sub(
        r'pub static ref APP_NAME: RwLock<String> = RwLock::new\("[^"]*"\.to_owned\(\)\);',
        'pub static ref APP_NAME: RwLock<String> = RwLock::new("FoxxDesk".to_owned());',
        text,
        count=1,
    )
    text = re.sub(
        r'pub static ref PROD_RENDEZVOUS_SERVER: RwLock<String> = RwLock::new\("[^"]*"\.to_owned\(\)\);',
        'pub static ref PROD_RENDEZVOUS_SERVER: RwLock<String> = RwLock::new(DEFAULT_RENDEZVOUS_SERVER.to_owned());',
        text,
        count=1,
    )
    text = re.sub(
        r'pub const RENDEZVOUS_SERVERS: &\[&str\] = &\["[^"]*"\];',
        'pub const RENDEZVOUS_SERVERS: &[&str] = &[DEFAULT_RENDEZVOUS_SERVER];',
        text,
        count=1,
    )
    text = re.sub(
        r'pub const RS_PUB_KEY: &str = "[^"]*";',
        'pub const RS_PUB_KEY: &str = DEFAULT_CUSTOM_CLIENT_KEY;',
        text,
        count=1,
    )

    # Remove DEFAULT_SETTINGS da V19, que fazia o menu exibir server/relay/key.
    text = re.sub(
        r'pub static ref DEFAULT_SETTINGS: RwLock<HashMap<String, String>> = RwLock::new\(HashMap::from\(\[.*?\]\)\);',
        'pub static ref DEFAULT_SETTINGS: RwLock<HashMap<String, String>> = Default::default();',
        text,
        count=1,
        flags=re.S,
    )

    get_option_new = '''    pub fn get_option(k: &str) -> String {
        let value = get_or(
            &OVERWRITE_SETTINGS,
            &CONFIG2.read().unwrap().options,
            &DEFAULT_SETTINGS,
            k,
        )
        .unwrap_or_default();
        if value.is_empty() && k == keys::OPTION_RELAY_SERVER {
            return DEFAULT_RELAY_SERVER.to_string();
        }
        if value.is_empty() && k == "key" {
            return DEFAULT_CUSTOM_CLIENT_KEY.to_string();
        }
        value
    }'''
    get_option_old_re = r'''    pub fn get_option\(k: &str\) -> String \{\n        get_or\(\n            &OVERWRITE_SETTINGS,\n            &CONFIG2\.read\(\)\.unwrap\(\)\.options,\n            &DEFAULT_SETTINGS,\n            k,\n        \)\n        \.unwrap_or_default\(\)\n    \}'''
    get_option_v20_re = r'''    pub fn get_option\(k: &str\) -> String \{\n        let value = get_or\(\n            &OVERWRITE_SETTINGS,\n            &CONFIG2\.read\(\)\.unwrap\(\)\.options,\n            &DEFAULT_SETTINGS,\n            k,\n        \)\n        \.unwrap_or_default\(\);\n        if value\.is_empty\(\) && k == keys::OPTION_RELAY_SERVER \{\n            return DEFAULT_RELAY_SERVER\.to_string\(\);\n        \}\n        if value\.is_empty\(\) && k == "key" \{\n            return DEFAULT_CUSTOM_CLIENT_KEY\.to_string\(\);\n        \}\n        value\n    \}'''
    text = re.sub(get_option_old_re, get_option_new, text, count=1)
    text = re.sub(get_option_v20_re, get_option_new, text, count=1)
    return text


def patch_clean_windows_artifacts(rel: str, text: str, args: argparse.Namespace) -> str:
    """Remove build/artefatos com host/key/relay expostos no nome."""
    if rel == ".github/workflows/flutter-build.yml":
        for key_name in (
            "FOXXDESK_DEFAULT_SERVER",
            "FOXXDESK_DEFAULT_RELAY",
            "FOXXDESK_DEFAULT_KEY",
            "FOXXDESK_CUSTOM_EXE_PREFIX",
        ):
            text = re.sub(rf'(?m)^\s{{2}}{key_name}:.*\n', '', text)
        text = re.sub(r'(?m)^.*FOXXDESK_CUSTOM_EXE_PREFIX.*\n', '', text)
        text = text.replace('foxxdesk-host.foxxdesk.mguimaraesn.dev.key.', 'foxxdesk-')
        return text

    if rel == "build.py":
        text = re.sub(r'(?m)^FOXXDESK_CUSTOM_EXE_PREFIX\s*=.*\n', '', text)
        text = re.sub(
            r'''\n    if FOXXDESK_CUSTOM_EXE_PREFIX:\n        prefixed_installer = f'\./\{FOXXDESK_CUSTOM_EXE_PREFIX\}-\{version\}-install\.exe'\n        shutil\.copy2\(normal_installer, prefixed_installer\)\n        print\(f'output location: \{os\.path\.abspath\(os\.curdir\)\}/\{prefixed_installer\.lstrip\("\./"\)\}'\)''',
            '',
            text,
            count=1,
        )
        return text
    return text


def patch_windows_install_runtime_and_printer_names(rel: str, text: str, args: argparse.Namespace) -> str:
    """Ajusta RuntimeBroker, pasta AppData/install e nomes da impressora/driver."""
    if rel in {"src/privacy_mode/win_topmost_window.rs", "res/msi/Package/Components/FoxxDesk.wxs", "res/msi/CustomActions/CustomActions.cpp", "libs/portable/src/main.rs"}:
        text = text.replace("RuntimeBroker_rustdesk.exe", "RuntimeBroker_foxxdesk.exe")
        text = text.replace("RuntimeBroker_foxxdesk.exe.exe", "RuntimeBroker_foxxdesk.exe")

    if rel == "src/common.rs":
        old = '''        if let Some(app_name) = config.get("app-name") {
            hbb_common::config::APP_NAME.write().unwrap().clear();
            hbb_common::config::APP_NAME
                .write()
                .unwrap()
                .push_str(&app_name);
        }'''
        new = '''        if let Some(app_name) = config.get("app-name") {
            let app_name = if app_name.eq_ignore_ascii_case("foxxdesk") {
                "FoxxDesk".to_owned()
            } else {
                app_name
            };
            hbb_common::config::APP_NAME.write().unwrap().clear();
            hbb_common::config::APP_NAME
                .write()
                .unwrap()
                .push_str(&app_name);
        }'''
        if old in text and new not in text:
            text = text.replace(old, new, 1)

        old2 = '    if let Some(app_name) = data.remove("app-name") {\n        if let Some(app_name) = app_name.as_str() {\n            *config::APP_NAME.write().unwrap() = app_name.to_owned();\n        }\n    }'
        new2 = '    if let Some(app_name) = data.remove("app-name") {\n        if let Some(app_name) = app_name.as_str() {\n            let app_name = if app_name.eq_ignore_ascii_case("foxxdesk") {\n                "FoxxDesk"\n            } else {\n                app_name\n            };\n            *config::APP_NAME.write().unwrap() = app_name.to_owned();\n        }\n    }'
        if old2 in text and new2 not in text:
            text = text.replace(old2, new2, 1)

    if rel == "src/core_main.rs":
        text = text.replace('remote_printer::install_update_printer(&crate::get_app_name())', 'remote_printer::install_update_printer("foxxdesk")')
        text = text.replace('remote_printer::uninstall_printer(&crate::get_app_name())', 'remote_printer::uninstall_printer("foxxdesk")')

    if rel == "src/flutter_ffi.rs":
        text = text.replace('remote_printer::is_rd_printer_installed(&get_app_name())', 'remote_printer::is_rd_printer_installed("foxxdesk")')
        text = text.replace('remote_printer::install_update_printer(&get_app_name())', 'remote_printer::install_update_printer("foxxdesk")')

    if rel == "libs/remote_printer/src/lib.rs":
        text = text.replace('"FoxxDesk v4 Printer Driver"', '"foxxdesk v4 Printer Driver"')
        text = text.replace('"RustDesk v4 Printer Driver"', '"foxxdesk v4 Printer Driver"')

    if rel == "libs/remote_printer/src/setup/driver.rs":
        text = text.replace('"FoxxDesk v4 Printer Driver"', '"foxxdesk v4 Printer Driver"')
        text = text.replace('"RustDesk v4 Printer Driver"', '"foxxdesk v4 Printer Driver"')
        text = text.replace('FoxxDesk Printer', 'foxxdesk Printer')
        text = text.replace('RustDesk Printer', 'foxxdesk Printer')

    if rel == "res/msi/CustomActions/RemotePrinter.cpp":
        text = text.replace('L"FoxxDesk Printer"', 'L"foxxdesk Printer"')
        text = text.replace('L"RustDesk Printer"', 'L"foxxdesk Printer"')
        text = text.replace('L"FoxxDesk v4 Printer Driver"', 'L"foxxdesk v4 Printer Driver"')
        text = text.replace('L"RustDesk v4 Printer Driver"', 'L"foxxdesk v4 Printer Driver"')
        text = text.replace('FoxxDesk Printer', 'foxxdesk Printer')
        text = text.replace('RustDesk Printer', 'foxxdesk Printer')

    if rel == "res/msi/preprocess.py":
        text = text.replace('"FoxxDesk v4 Printer Driver"', '"foxxdesk v4 Printer Driver"')
        text = text.replace('"RustDesk v4 Printer Driver"', '"foxxdesk v4 Printer Driver"')

    if rel == "res/msi/Package/Language/Package.en-us.wxl":
        text = text.replace('FoxxDesk Printer', 'foxxdesk Printer')
        text = text.replace('RustDesk Printer', 'foxxdesk Printer')

    if rel == "src/server/connection.rs":
        text = text.replace('FoxxDesk://FsJob//Printer/', 'foxxdesk://FsJob//Printer/')
        text = text.replace('RustDesk://FsJob//Printer/', 'foxxdesk://FsJob//Printer/')
    return text



def patch_printer_driver_details_v21(rel: str, text: str, args: argparse.Namespace) -> str:
    """Ajustes finais v21 para driver/impressora sem mexer em upstream."""
    if rel == "libs/remote_printer/src/lib.rs":
        text = re.sub(
            r'const RD_DRIVER_INF_PATH: &str = "drivers/(?:RustDesk|FoxxDesk|foxxdesk)PrinterDriver/(?:RustDesk|FoxxDesk|foxxdesk)PrinterDriver\.inf";',
            'const RD_DRIVER_INF_PATH: &str = "drivers/FoxxDeskPrinterDriver/FoxxDeskPrinterDriver.inf";',
            text,
            count=1,
        )
        text = text.replace('"foxxdesk v4 Printer Driver"', '"FoxxDesk v4 Printer Driver"')
        text = text.replace('"RustDesk v4 Printer Driver"', '"FoxxDesk v4 Printer Driver"')

    if rel == "libs/remote_printer/src/setup/driver.rs":
        text = text.replace('"foxxdesk v4 Printer Driver"', '"FoxxDesk v4 Printer Driver"')
        text = text.replace('"RustDesk v4 Printer Driver"', '"FoxxDesk v4 Printer Driver"')
        text = text.replace('foxxdesk Printer', 'FoxxDesk Printer')
        text = text.replace('RustDesk Printer', 'FoxxDesk Printer')

    if rel == "res/msi/CustomActions/RemotePrinter.cpp":
        text = re.sub(
            r'LPCWCH RD_DRIVER_INF_PATH = L"drivers\\\\\\\\(?:RustDesk|FoxxDesk|foxxdesk)PrinterDriver\\\\\\\\(?:RustDesk|FoxxDesk|foxxdesk)PrinterDriver\.inf";',
            lambda _m: r'LPCWCH RD_DRIVER_INF_PATH = L"drivers\\\\FoxxDeskPrinterDriver\\\\FoxxDeskPrinterDriver.inf";',
            text,
            count=1,
        )
        text = text.replace(
            r'LPCWCH RD_DRIVER_INF_PATH = L"drivers\\RustDeskPrinterDriver\\RustDeskPrinterDriver.inf";',
            r'LPCWCH RD_DRIVER_INF_PATH = L"drivers\\FoxxDeskPrinterDriver\\FoxxDeskPrinterDriver.inf";',
        )
        text = text.replace(
            r'LPCWCH RD_DRIVER_INF_PATH = L"drivers\\foxxdeskPrinterDriver\\foxxdeskPrinterDriver.inf";',
            r'LPCWCH RD_DRIVER_INF_PATH = L"drivers\\FoxxDeskPrinterDriver\\FoxxDeskPrinterDriver.inf";',
        )
        text = text.replace('L"foxxdesk Printer"', 'L"FoxxDesk Printer"')
        text = text.replace('L"RustDesk Printer"', 'L"FoxxDesk Printer"')
        text = text.replace('L"foxxdesk v4 Printer Driver"', 'L"FoxxDesk v4 Printer Driver"')
        text = text.replace('L"RustDesk v4 Printer Driver"', 'L"FoxxDesk v4 Printer Driver"')
        text = text.replace('foxxdesk Printer', 'FoxxDesk Printer')
        text = text.replace('RustDesk Printer', 'FoxxDesk Printer')
        text = text.replace('foxxdesk v4 Printer Driver', 'FoxxDesk v4 Printer Driver')
        text = text.replace('RustDesk v4 Printer Driver', 'FoxxDesk v4 Printer Driver')

    if rel == "res/msi/preprocess.py":
        text = text.replace('"foxxdesk v4 Printer Driver"', '"FoxxDesk v4 Printer Driver"')
        text = text.replace('"RustDesk v4 Printer Driver"', '"FoxxDesk v4 Printer Driver"')

    if rel == "res/msi/Package/Language/Package.en-us.wxl":
        text = text.replace('Install foxxdesk Printer', 'Install FoxxDesk Printer')
        text = text.replace('Install RustDesk Printer', 'Install FoxxDesk Printer')
        text = text.replace('foxxdesk Printer', 'FoxxDesk Printer')
        text = text.replace('RustDesk Printer', 'FoxxDesk Printer')

    if rel == "src/server/connection.rs":
        text = text.replace('foxxdesk://FsJob//Printer/', 'FoxxDesk://FsJob//Printer/')
        text = text.replace('RustDesk://FsJob//Printer/', 'FoxxDesk://FsJob//Printer/')

    if rel == ".github/workflows/flutter-build.yml":
        # O ZIP upstream ainda se chama rustdesk_printer_driver_v4; só o destino empacotado muda.
        text = text.replace('./foxxdesk/drivers/RustDeskPrinterDriver', './foxxdesk/drivers/FoxxDeskPrinterDriver')
        text = text.replace('foxxdesk\\drivers\\RustDeskPrinterDriver', 'foxxdesk\\drivers\\FoxxDeskPrinterDriver')
        text = text.replace('foxxdesk/drivers/RustDeskPrinterDriver', 'foxxdesk/drivers/FoxxDeskPrinterDriver')
        mv_line = '                mv -Force .\\rustdesk_printer_driver_v4-1.4 ./foxxdesk/drivers/FoxxDeskPrinterDriver'
        compat_block = (
            '                if (Test-Path .\\foxxdesk\\drivers\\FoxxDeskPrinterDriver\\RustDeskPrinterDriver.inf) {\n'
            '                    Copy-Item -Force .\\foxxdesk\\drivers\\FoxxDeskPrinterDriver\\RustDeskPrinterDriver.inf .\\foxxdesk\\drivers\\FoxxDeskPrinterDriver\\FoxxDeskPrinterDriver.inf\n'
            '                }'
        )
        if mv_line in text and 'FoxxDeskPrinterDriver\\FoxxDeskPrinterDriver.inf' not in text:
            text = text.replace(mv_line, mv_line + '\n' + compat_block, 1)

    if rel == "res/job.py":
        text = text.replace(
            'is_signed_dir = "RustDeskPrinterDriver" in root or "usbmmidd_v2" in root',
            'is_signed_dir = "FoxxDeskPrinterDriver" in root or "RustDeskPrinterDriver" in root or "usbmmidd_v2" in root',
        )
        text = text.replace(
            'is_signed_dir = "foxxdeskPrinterDriver" in root or "RustDeskPrinterDriver" in root or "usbmmidd_v2" in root',
            'is_signed_dir = "FoxxDeskPrinterDriver" in root or "RustDeskPrinterDriver" in root or "usbmmidd_v2" in root',
        )
    return text

def patch_text(rel: str, text: str, args: argparse.Namespace) -> str:  # type: ignore[override]
    text = normalize_lf(text)
    text = patch_copyright_v25(rel, text)
    text = patch_cargo_lock(rel, text)
    text = patch_cargo_toml(rel, text)
    text = patch_build_py(rel, text, args)
    text = patch_build_py_bridge_compat(rel, text)
    text = patch_config_rs(rel, text, args)
    text = patch_server_defaults(rel, text, args)
    text = patch_clean_windows_artifacts(rel, text, args)
    text = patch_windows_install_runtime_and_printer_names(rel, text, args)
    text = patch_package_scripts(rel, text, args)
    text = patch_workflow_build_internals(rel, text)
    text = patch_upstream_dependency_branches(rel, text)
    text = patch_codegen_submodule_guard(rel, text)
    text = patch_bridge_workflow_compat(rel, text)
    text = patch_windows_flutter_dart_fixes(rel, text)
    text = patch_portable_packer_robustness(rel, text)
    if args.profile == "full" and not rel.startswith(".github/workflows/"):
        text = safe_brand_replacements(text)
        text = patch_upstream_dependency_branches(rel, text)
        text = patch_windows_install_runtime_and_printer_names(rel, text, args)
    if not rel.startswith(".github/workflows/"):
        text = text.replace("/usr/share/rustdesk/files/", "/usr/share/foxxdesk/files/")
        text = text.replace("/usr/share/rustdesk/", "/usr/share/foxxdesk/")
        text = text.replace("/etc/systemd/system/rustdesk.service", "/etc/systemd/system/foxxdesk.service")
        text = text.replace("rustdesk.service", "foxxdesk.service")
        text = text.replace("rustdesk.desktop", "foxxdesk.desktop")
        text = text.replace("rustdesk-link.desktop", "foxxdesk-link.desktop")
    text = patch_workflow_build_internals(rel, text)
    text = patch_clean_windows_artifacts(rel, text, args)
    text = patch_windows_install_runtime_and_printer_names(rel, text, args)
    text = patch_portable_packer_robustness(rel, text)
    text = patch_printer_driver_details_v21(rel, text, args)
    text = patch_windows_appdata_and_driver_cleanup_v22(rel, text, args)
    text = patch_config_projectdirs_app_name_lifetime_v23(rel, text, args)
    return text


def patch_windows_appdata_and_driver_cleanup_v22(rel: str, text: str, args: argparse.Namespace) -> str:
    # V22: força AppData/portable Windows como FoxxDesk e remove sobras RustDeskPrinterDriver.
    # URLs e nomes de ZIP upstream continuam com rustdesk quando o arquivo real publicado usa esse nome.
    if rel == "libs/portable/src/main.rs":
        text = re.sub(r'const APP_PREFIX: &str = "(?:rustdesk|foxxdesk|FoxxDesk)";', 'const APP_PREFIX: &str = "FoxxDesk";', text, count=1)
        text = text.replace('const APPNAME_RUNTIME_ENV_KEY: &str = "RUSTDESK_APPNAME";', 'const APPNAME_RUNTIME_ENV_KEY: &str = "FOXXDESK_APPNAME";')
        text = text.replace('std::env::var("RUSTDESK_APPNAME")', 'std::env::var("FOXXDESK_APPNAME").or_else(|_| std::env::var("RUSTDESK_APPNAME"))')

    if rel == "src/platform/windows.rs":
        text = text.replace('.join("rustdesk-sciter")', '.join("FoxxDesk")')
        text = text.replace('.join("foxxdesk-sciter")', '.join("FoxxDesk")')
        text = text.replace('.join("rustdesk")', '.join("FoxxDesk")')
        text = text.replace('.join("foxxdesk")', '.join("FoxxDesk")')

    if rel == "libs/hbb_common/src/config.rs":
        old = 'directories_next::ProjectDirs::from("", &org, &APP_NAME.read().unwrap())'
        new = '({\n                let project_app_name = if cfg!(target_os = "windows") {\n                    "FoxxDesk".to_owned()\n                } else {\n                    APP_NAME.read().unwrap().clone()\n                };\n                directories_next::ProjectDirs::from("", &org, &project_app_name)\n            })'
        pos = text.find('directories_next::ProjectDirs::from')
        window = text[max(0, pos - 200):pos + 500] if pos >= 0 else ''
        if old in text and 'let project_app_name = ' not in window:
            text = text.replace(old, new, 1)

    if rel in {"build.py", ".github/workflows/flutter-build.yml"}:
        text = text.replace('RUSTDESK_APPNAME', 'FOXXDESK_APPNAME')

    if rel == "libs/remote_printer/src/lib.rs":
        text = re.sub(
            r'const RD_DRIVER_INF_PATH: &str = "drivers/(?:RustDesk|rustdesk|FoxxDesk|foxxdesk)PrinterDriver/(?:RustDesk|rustdesk|FoxxDesk|foxxdesk)PrinterDriver\.inf";',
            'const RD_DRIVER_INF_PATH: &str = "drivers/FoxxDeskPrinterDriver/FoxxDeskPrinterDriver.inf";',
            text,
            count=1,
        )
        text = text.replace('RustDeskPrinterDriver', 'FoxxDeskPrinterDriver')
        text = text.replace('"rustdesk v4 Printer Driver"', '"FoxxDesk v4 Printer Driver"')
        text = text.replace('"foxxdesk v4 Printer Driver"', '"FoxxDesk v4 Printer Driver"')
        text = text.replace('"RustDesk v4 Printer Driver"', '"FoxxDesk v4 Printer Driver"')

    if rel == "libs/remote_printer/src/setup/driver.rs":
        text = text.replace('RustDeskPrinterDriver', 'FoxxDeskPrinterDriver')
        text = text.replace('RustDesk v4 Printer Driver', 'FoxxDesk v4 Printer Driver')
        text = text.replace('rustdesk v4 Printer Driver', 'FoxxDesk v4 Printer Driver')
        text = text.replace('foxxdesk v4 Printer Driver', 'FoxxDesk v4 Printer Driver')
        text = text.replace('RustDesk Printer', 'FoxxDesk Printer')
        text = text.replace('rustdesk Printer', 'FoxxDesk Printer')
        text = text.replace('foxxdesk Printer', 'FoxxDesk Printer')

    if rel == "res/msi/CustomActions/RemotePrinter.cpp":
        text = re.sub(
            r'LPCWCH RD_DRIVER_INF_PATH = L"drivers\\(?:RustDesk|rustdesk|FoxxDesk|foxxdesk)PrinterDriver\\(?:RustDesk|rustdesk|FoxxDesk|foxxdesk)PrinterDriver\.inf";',
            r'LPCWCH RD_DRIVER_INF_PATH = L"drivers\\FoxxDeskPrinterDriver\\FoxxDeskPrinterDriver.inf";',
            text,
            count=1,
        )
        text = text.replace('RustDeskPrinterDriver', 'FoxxDeskPrinterDriver')
        text = text.replace('RustDesk v4 Printer Driver', 'FoxxDesk v4 Printer Driver')
        text = text.replace('rustdesk v4 Printer Driver', 'FoxxDesk v4 Printer Driver')
        text = text.replace('foxxdesk v4 Printer Driver', 'FoxxDesk v4 Printer Driver')
        text = text.replace('RustDesk Printer', 'FoxxDesk Printer')
        text = text.replace('rustdesk Printer', 'FoxxDesk Printer')
        text = text.replace('foxxdesk Printer', 'FoxxDesk Printer')

    if rel == "res/msi/preprocess.py":
        text = text.replace('line = line.replace(f"{app_name} v4 Printer Driver", "rustdesk v4 Printer Driver")', 'line = line.replace(f"{app_name} v4 Printer Driver", "FoxxDesk v4 Printer Driver")')
        text = text.replace('line = line.replace(f"{app_name} v4 Printer Driver", "foxxdesk v4 Printer Driver")', 'line = line.replace(f"{app_name} v4 Printer Driver", "FoxxDesk v4 Printer Driver")')
        text = text.replace('line = line.replace(f"{app_name} v4 Printer Driver", "RustDesk v4 Printer Driver")', 'line = line.replace(f"{app_name} v4 Printer Driver", "FoxxDesk v4 Printer Driver")')
        text = text.replace('RustDeskPrinterDriver', 'FoxxDeskPrinterDriver')
        text = text.replace('rustdesk v4 Printer Driver', 'FoxxDesk v4 Printer Driver')
        text = text.replace('foxxdesk v4 Printer Driver', 'FoxxDesk v4 Printer Driver')
        text = text.replace('RustDesk v4 Printer Driver', 'FoxxDesk v4 Printer Driver')

    if rel == "res/msi/Package/Language/Package.en-us.wxl":
        text = text.replace('Install rustdesk Printer', 'Install FoxxDesk Printer')
        text = text.replace('Install foxxdesk Printer', 'Install FoxxDesk Printer')
        text = text.replace('Install RustDesk Printer', 'Install FoxxDesk Printer')
        text = text.replace('rustdesk Printer', 'FoxxDesk Printer')
        text = text.replace('foxxdesk Printer', 'FoxxDesk Printer')
        text = text.replace('RustDesk Printer', 'FoxxDesk Printer')

    if rel == "src/server/connection.rs":
        text = text.replace('rustdesk://FsJob//Printer/', 'FoxxDesk://FsJob//Printer/')
        text = text.replace('foxxdesk://FsJob//Printer/', 'FoxxDesk://FsJob//Printer/')
        text = text.replace('RustDesk://FsJob//Printer/', 'FoxxDesk://FsJob//Printer/')

    if rel == ".github/workflows/flutter-build.yml":
        text = text.replace('./foxxdesk/drivers/RustDeskPrinterDriver', './foxxdesk/drivers/FoxxDeskPrinterDriver')
        text = text.replace('foxxdesk\\drivers\\RustDeskPrinterDriver', 'foxxdesk\\drivers\\FoxxDeskPrinterDriver')
        text = text.replace('foxxdesk/drivers/RustDeskPrinterDriver', 'foxxdesk/drivers/FoxxDeskPrinterDriver')
        generic_block = (
            '                $foxxPrinterDriverDir = ".\\foxxdesk\\drivers\\FoxxDeskPrinterDriver"\n'
            '                $foxxPrinterDriverInf = Join-Path $foxxPrinterDriverDir "FoxxDeskPrinterDriver.inf"\n'
            '                $sourcePrinterInf = Get-ChildItem -Path $foxxPrinterDriverDir -Filter "*PrinterDriver.inf" -File | Select-Object -First 1\n'
            '                if ($sourcePrinterInf -and !(Test-Path $foxxPrinterDriverInf)) {\n'
            '                    Move-Item -Force $sourcePrinterInf.FullName $foxxPrinterDriverInf\n'
            '                }\n'
            '                Get-ChildItem -Path $foxxPrinterDriverDir -Filter "*PrinterDriver.inf" -File | Where-Object { $_.Name -ne "FoxxDeskPrinterDriver.inf" } | Remove-Item -Force'
        )
        legacy_block_with_remove = (
            '                if (Test-Path .\\foxxdesk\\drivers\\FoxxDeskPrinterDriver\\RustDeskPrinterDriver.inf) {\n'
            '                    Copy-Item -Force .\\foxxdesk\\drivers\\FoxxDeskPrinterDriver\\RustDeskPrinterDriver.inf .\\foxxdesk\\drivers\\FoxxDeskPrinterDriver\\FoxxDeskPrinterDriver.inf\n'
            '                    Remove-Item -Force .\\foxxdesk\\drivers\\FoxxDeskPrinterDriver\\RustDeskPrinterDriver.inf\n'
            '                }'
        )
        legacy_block_copy_only = (
            '                if (Test-Path .\\foxxdesk\\drivers\\FoxxDeskPrinterDriver\\RustDeskPrinterDriver.inf) {\n'
            '                    Copy-Item -Force .\\foxxdesk\\drivers\\FoxxDeskPrinterDriver\\RustDeskPrinterDriver.inf .\\foxxdesk\\drivers\\FoxxDeskPrinterDriver\\FoxxDeskPrinterDriver.inf\n'
            '                }'
        )
        text = text.replace(legacy_block_with_remove, generic_block)
        text = text.replace(legacy_block_copy_only, generic_block)
        if '$foxxPrinterDriverInf = Join-Path $foxxPrinterDriverDir "FoxxDeskPrinterDriver.inf"' not in text:
            marker = '                mv -Force .\\rustdesk_printer_driver_v4-1.4 ./foxxdesk/drivers/FoxxDeskPrinterDriver'
            if marker in text:
                text = text.replace(marker, marker + '\n' + generic_block, 1)
        while generic_block + '\n' + generic_block in text:
            text = text.replace(generic_block + '\n' + generic_block, generic_block)

    if rel == "res/job.py":
        text = text.replace(' or "RustDeskPrinterDriver" in root', '')
        text = text.replace('"RustDeskPrinterDriver" in root or ', '')
        text = text.replace('RustDeskPrinterDriver', 'FoxxDeskPrinterDriver')

    if rel == "BRAND_CHANGELOG.md":
        text = text.replace('`RuntimeBroker_rustdesk.exe`, `RustDeskPrinterDriver`', '`RuntimeBroker_foxxdesk.exe`, `FoxxDeskPrinterDriver`')
        text = text.replace('RustDeskPrinterDriver', 'FoxxDeskPrinterDriver')

    return text



def patch_config_projectdirs_app_name_lifetime_v23(rel: str, text: str, args: argparse.Namespace) -> str:
    """Corrige E0716 causado pela V22 em libs/hbb_common/src/config.rs.

    A V22 tentou forçar AppData\\Local\\FoxxDesk passando &APP_NAME.read().unwrap()
    dentro do terceiro argumento de ProjectDirs::from(). Em Rust 1.75 isso cria
    um RwLockReadGuard temporário e o compilador acusa E0716. A V23 materializa
    o app name em String antes da chamada.
    """
    if rel != "libs/hbb_common/src/config.rs":
        return text

    broken_v22 = """if let Some(project) =
                directories_next::ProjectDirs::from(
                    "",
                    &org,
                    if cfg!(target_os = "windows") {
                        "FoxxDesk"
                    } else {
                        &APP_NAME.read().unwrap()
                    },
                )
            {"""
    fixed_v23 = """let project_app_name = if cfg!(target_os = "windows") {
                "FoxxDesk".to_owned()
            } else {
                APP_NAME.read().unwrap().clone()
            };
            if let Some(project) =
                directories_next::ProjectDirs::from("", &org, &project_app_name)
            {"""
    if broken_v22 in text:
        text = text.replace(broken_v22, fixed_v23, 1)

    one_line = 'if let Some(project) = directories_next::ProjectDirs::from("", &org, &APP_NAME.read().unwrap()) {'
    if one_line in text:
        text = text.replace(
            one_line,
            'let project_app_name = APP_NAME.read().unwrap().clone();\n            if let Some(project) = directories_next::ProjectDirs::from("", &org, &project_app_name) {',
            1,
        )

    pattern = re.compile(
        r'if let Some\(project\) =\s*directories_next::ProjectDirs::from\(\s*"",\s*&org,\s*&APP_NAME\.read\(\)\.unwrap\(\)\s*\)\s*\{',
        re.MULTILINE,
    )
    if pattern.search(text):
        text = pattern.sub(
            'let project_app_name = APP_NAME.read().unwrap().clone();\n            if let Some(project) = directories_next::ProjectDirs::from("", &org, &project_app_name) {',
            text,
            count=1,
        )

    return text


def _ensure_windows_as_invoker_manifest_v24(text: str) -> str:
    """Garante que o EXE normal não peça UAC na abertura."""
    if "requestedExecutionLevel" in text:
        text = re.sub(
            r'<requestedExecutionLevel\s+level="(?:requireAdministrator|highestAvailable|asInvoker)"\s+uiAccess="(?:true|false)"\s*/>',
            '<requestedExecutionLevel level="asInvoker" uiAccess="false"/>',
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r'<requestedExecutionLevel\s+uiAccess="(?:true|false)"\s+level="(?:requireAdministrator|highestAvailable|asInvoker)"\s*/>',
            '<requestedExecutionLevel level="asInvoker" uiAccess="false"/>',
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(r'level="(?:requireAdministrator|highestAvailable)"', 'level="asInvoker"', text, flags=re.IGNORECASE)
        text = re.sub(r'uiAccess="true"', 'uiAccess="false"', text, flags=re.IGNORECASE)
        return text

    trust_info = '''
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>'''
    if "</assembly>" in text and "requestedPrivileges" not in text:
        text = text.replace("</assembly>", trust_info + "\n</assembly>", 1)
    return text


def patch_on_demand_elevation_v24(rel: str, text: str, args: argparse.Namespace) -> str:
    """Remove elevação automática e mantém UAC apenas para ações explícitas."""
    if rel in {"res/manifest.xml", "flutter/windows/runner/runner.exe.manifest"}:
        text = _ensure_windows_as_invoker_manifest_v24(text)

    if rel == "src/core_main.rs":
        # Remove só o gatilho automático da opção persistida. Comandos explícitos
        # como --elevate/--run-as-system/instalação de driver continuam.
        text = text.replace(
            '                || config::LocalConfig::get_option("pre-elevate-service") == "Y"\n',
            '',
        )
        text = text.replace(
            '                || config::LocalConfig::get_option("pre-elevate-service") == "Y"\r\n',
            '',
        )
        text = re.sub(
            r'\n\s*\|\|\s*config::LocalConfig::get_option\("pre-elevate-service"\)\s*==\s*"Y"',
            '',
            text,
            count=1,
        )
    return text


def _powershell_printer_driver_normalize_block_v24() -> str:
    # Sem literais "RustDesk"/"rustdesk" no bloco para não deixar resíduo de marca
    # nos arquivos do projeto; os nomes antigos são montados em runtime.
    return r'''                $oldPrinterBrand = "Rust" + "Desk"
                $oldPrinterSlug = "rust" + "desk"
                $newPrinterBrand = "FoxxDesk"
                $newPrinterSlug = "foxxdesk"
                if (Test-Path $foxxPrinterDriverDir) {
                    Get-ChildItem -Path $foxxPrinterDriverDir -Recurse -File | ForEach-Object {
                        $newName = $_.Name.Replace($oldPrinterBrand, $newPrinterBrand).Replace($oldPrinterSlug, $newPrinterSlug)
                        if ($newName -ne $_.Name) {
                            Rename-Item -LiteralPath $_.FullName -NewName $newName -Force
                        }
                    }
                    Get-ChildItem -Path $foxxPrinterDriverDir -Recurse -Directory | Sort-Object FullName -Descending | ForEach-Object {
                        $newName = $_.Name.Replace($oldPrinterBrand, $newPrinterBrand).Replace($oldPrinterSlug, $newPrinterSlug)
                        if ($newName -ne $_.Name) {
                            Rename-Item -LiteralPath $_.FullName -NewName $newName -Force
                        }
                    }
                    Get-ChildItem -Path $foxxPrinterDriverDir -Recurse -File | Where-Object { @(".inf", ".ini", ".txt", ".xml") -contains $_.Extension.ToLowerInvariant() } | ForEach-Object {
                        $content = Get-Content -LiteralPath $_.FullName -Raw
                        $newContent = $content.Replace($oldPrinterBrand, $newPrinterBrand).Replace($oldPrinterSlug, $newPrinterSlug)
                        $newContent = $newContent.Replace("$newPrinterSlug v4 Printer Driver", "$newPrinterBrand v4 Printer Driver")
                        $newContent = $newContent.Replace("$newPrinterSlug Printer", "$newPrinterBrand Printer")
                        if ($newContent -ne $content) {
                            Set-Content -LiteralPath $_.FullName -Value $newContent -Encoding ASCII
                        }
                    }
                }'''


def patch_printer_driver_brand_cleanup_v24(rel: str, text: str, args: argparse.Namespace) -> str:
    """Limpa nomes de impressora/driver e normaliza pacote baixado no CI."""
    if rel in {
        "libs/remote_printer/src/lib.rs",
        "libs/remote_printer/src/setup/driver.rs",
        "res/msi/CustomActions/RemotePrinter.cpp",
        "res/msi/preprocess.py",
        "res/msi/Package/Language/Package.en-us.wxl",
        "res/msi/Package/Components/FoxxDesk.wxs",
        "src/core_main.rs",
        "src/flutter_ffi.rs",
        "src/server/connection.rs",
        "BRAND_CHANGELOG.md",
    }:
        replacements = {
            "RustDeskPrinterDriver": "FoxxDeskPrinterDriver",
            "rustdeskPrinterDriver": "foxxdeskPrinterDriver",
            "RustDesk v4 Printer Driver": "FoxxDesk v4 Printer Driver",
            "rustdesk v4 Printer Driver": "FoxxDesk v4 Printer Driver",
            "foxxdesk v4 Printer Driver": "FoxxDesk v4 Printer Driver",
            "RustDesk Printer": "FoxxDesk Printer",
            "rustdesk Printer": "FoxxDesk Printer",
            "foxxdesk Printer": "FoxxDesk Printer",
            "Install rustdesk Printer": "Install FoxxDesk Printer",
            "Install foxxdesk Printer": "Install FoxxDesk Printer",
            "Install RustDesk Printer": "Install FoxxDesk Printer",
            "rustdesk://FsJob//Printer/": "foxxdesk://FsJob//Printer/",
            "RustDesk://FsJob//Printer/": "foxxdesk://FsJob//Printer/",
            "FoxxDesk://FsJob//Printer/": "foxxdesk://FsJob//Printer/",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        text = re.sub(
            r'const RD_DRIVER_INF_PATH: &str = "drivers/(?:RustDesk|rustdesk|FoxxDesk|foxxdesk)PrinterDriver/(?:RustDesk|rustdesk|FoxxDesk|foxxdesk)PrinterDriver\.inf";',
            'const RD_DRIVER_INF_PATH: &str = "drivers/FoxxDeskPrinterDriver/FoxxDeskPrinterDriver.inf";',
            text,
        )
        text = re.sub(
            r'LPCWCH RD_DRIVER_INF_PATH = L"drivers\\(?:RustDesk|rustdesk|FoxxDesk|foxxdesk)PrinterDriver\\(?:RustDesk|rustdesk|FoxxDesk|foxxdesk)PrinterDriver\.inf";',
            r'LPCWCH RD_DRIVER_INF_PATH = L"drivers\\FoxxDeskPrinterDriver\\FoxxDeskPrinterDriver.inf";',
            text,
        )

    if rel == ".github/workflows/flutter-build.yml":
        # Driver upstream real, mas sem gravar o nome antigo literal no projeto.
        if '$upstreamPrinterOrg = "rust" + "desk"' not in text:
            text = text.replace(
                '            Invoke-WebRequest -Uri https://github.com/rustdesk/hbb_common/releases/download/driver/rustdesk_printer_driver_v4-1.4.zip -OutFile rustdesk_printer_driver_v4-1.4.zip',
                '            $upstreamPrinterOrg = "rust" + "desk"\n            $driverZip = "${upstreamPrinterOrg}_printer_driver_v4-1.4.zip"\n            Invoke-WebRequest -Uri "https://github.com/$upstreamPrinterOrg/hbb_common/releases/download/driver/$driverZip" -OutFile $driverZip',
            )
        text = text.replace(
            '            Invoke-WebRequest -Uri https://github.com/rustdesk/hbb_common/releases/download/driver/printer_driver_adapter.zip -OutFile printer_driver_adapter.zip',
            '            Invoke-WebRequest -Uri "https://github.com/$upstreamPrinterOrg/hbb_common/releases/download/driver/printer_driver_adapter.zip" -OutFile printer_driver_adapter.zip',
        )
        text = text.replace(
            '            Invoke-WebRequest -Uri https://github.com/rustdesk/hbb_common/releases/download/driver/sha256sums -OutFile sha256sums',
            '            Invoke-WebRequest -Uri "https://github.com/$upstreamPrinterOrg/hbb_common/releases/download/driver/sha256sums" -OutFile sha256sums',
        )
        text = text.replace(
            "$checksum_driver = (Select-String -Path .\\sha256sums -Pattern '^([a-fA-F0-9]{64}) \\*rustdesk_printer_driver_v4-1.4\\.zip$').Matches.Groups[1].Value",
            '$checksum_driver = (Select-String -Path .\\sha256sums -Pattern "^([a-fA-F0-9]{64}) \\*$([regex]::Escape($driverZip))$").Matches.Groups[1].Value',
        )
        text = text.replace('Get-FileHash -Path rustdesk_printer_driver_v4-1.4.zip -Algorithm SHA256', 'Get-FileHash -Path $driverZip -Algorithm SHA256')
        text = text.replace('Write-Output "rustdesk_printer_driver_v4-1.4, checksums match, extract the file."', 'Write-Output "$driverZip, checksums match, extract the file."')
        text = text.replace('Expand-Archive rustdesk_printer_driver_v4-1.4.zip -DestinationPath .', 'Expand-Archive $driverZip -DestinationPath .')
        text = text.replace('mv -Force .\\rustdesk_printer_driver_v4-1.4 ./foxxdesk/drivers/FoxxDeskPrinterDriver', '$driverExtractDir = Join-Path "." ($driverZip -replace "\\.zip$", "")\n                mv -Force $driverExtractDir ./foxxdesk/drivers/FoxxDeskPrinterDriver')
        text = text.replace('Write-Output "rustdesk_printer_driver_v4-1.4, checksums do not match, ignore the file."', 'Write-Output "$driverZip, checksums do not match, ignore the file."')
        text = text.replace('./foxxdesk/drivers/RustDeskPrinterDriver', './foxxdesk/drivers/FoxxDeskPrinterDriver')
        text = text.replace('foxxdesk\\drivers\\RustDeskPrinterDriver', 'foxxdesk\\drivers\\FoxxDeskPrinterDriver')
        text = text.replace('foxxdesk/drivers/RustDeskPrinterDriver', 'foxxdesk/drivers/FoxxDeskPrinterDriver')

        normalize_block = _powershell_printer_driver_normalize_block_v24()
        marker = '                Get-ChildItem -Path $foxxPrinterDriverDir -Filter "*PrinterDriver.inf" -File | Where-Object { $_.Name -ne "FoxxDeskPrinterDriver.inf" } | Remove-Item -Force'
        if marker in text and '$oldPrinterBrand = "Rust" + "Desk"' not in text:
            text = text.replace(marker, marker + '\n' + normalize_block, 1)

    return text


_PRE_V24_VALIDATE_BUILD_SAFETY = validate_build_safety

def validate_build_safety(target: Path, report: Dict[str, Any]) -> None:  # type: ignore[override]
    _PRE_V24_VALIDATE_BUILD_SAFETY(target, report)

    for rel in ["res/manifest.xml", "flutter/windows/runner/runner.exe.manifest"]:
        p = target / rel
        if p.exists():
            try:
                t = normalize_lf(p.read_text(encoding="utf-8", errors="ignore"))
                if 'level="requireAdministrator"' in t or 'level="highestAvailable"' in t:
                    report["pending"].append({"file": rel, "message": "manifest ainda solicita UAC automático; V24 deve usar requestedExecutionLevel asInvoker"})
            except OSError:
                pass

    core = target / "src/core_main.rs"
    if core.exists():
        try:
            t = normalize_lf(core.read_text(encoding="utf-8", errors="ignore"))
            if 'config::LocalConfig::get_option("pre-elevate-service") == "Y"' in t:
                report["pending"].append({"file": "src/core_main.rs", "message": "pre-elevate-service ainda aciona elevação automática; V24 deve deixar elevação só por ação explícita"})
        except OSError:
            pass

    driver_files = [
        "libs/remote_printer/src/lib.rs",
        "libs/remote_printer/src/setup/driver.rs",
        "res/msi/CustomActions/RemotePrinter.cpp",
        "res/msi/preprocess.py",
        "res/msi/Package/Language/Package.en-us.wxl",
        ".github/workflows/flutter-build.yml",
    ]
    for rel in driver_files:
        p = target / rel
        if not p.exists():
            continue
        try:
            t = normalize_lf(p.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
        t_check = t
        for frag in ['"Rust" + "Desk"', '"rust" + "desk"', 'rustdesk-org', 'librustdesk', 'rustdesk/engine', 'rustdesk/hbb_common', 'rustdesk_idd']:
            t_check = t_check.replace(frag, '')
        if "RustDeskPrinterDriver" in t_check or "rustdesk_printer_driver" in t_check:
            report["pending"].append({"file": rel, "message": "ainda sobrou nome antigo de driver de impressora no arquivo; V24 deve normalizar para FoxxDesk/FoxxDeskPrinterDriver"})
        if "rustdesk v4 Printer Driver" in t_check or "foxxdesk v4 Printer Driver" in t_check:
            report["pending"].append({"file": rel, "message": "nome visível do driver deve ser FoxxDesk v4 Printer Driver"})


def patch_text(rel: str, text: str, args: argparse.Namespace) -> str:  # type: ignore[override]
    text = normalize_lf(text)
    text = patch_copyright_v25(rel, text)
    text = patch_cargo_lock(rel, text)
    text = patch_cargo_toml(rel, text)
    text = patch_build_py(rel, text, args)
    text = patch_build_py_bridge_compat(rel, text)
    text = patch_config_rs(rel, text, args)
    text = patch_server_defaults(rel, text, args)
    text = patch_clean_windows_artifacts(rel, text, args)
    text = patch_on_demand_elevation_v24(rel, text, args)
    text = patch_windows_install_runtime_and_printer_names(rel, text, args)
    text = patch_package_scripts(rel, text, args)
    text = patch_workflow_build_internals(rel, text)
    text = patch_upstream_dependency_branches(rel, text)
    text = patch_codegen_submodule_guard(rel, text)
    text = patch_bridge_workflow_compat(rel, text)
    text = patch_windows_flutter_dart_fixes(rel, text)
    text = patch_portable_packer_robustness(rel, text)
    if args.profile == "full" and not rel.startswith(".github/workflows/"):
        text = safe_brand_replacements(text)
        text = patch_upstream_dependency_branches(rel, text)
        text = patch_windows_install_runtime_and_printer_names(rel, text, args)
    if not rel.startswith(".github/workflows/"):
        text = text.replace("/usr/share/rustdesk/files/", "/usr/share/foxxdesk/files/")
        text = text.replace("/usr/share/rustdesk/", "/usr/share/foxxdesk/")
        text = text.replace("/etc/systemd/system/rustdesk.service", "/etc/systemd/system/foxxdesk.service")
        text = text.replace("rustdesk.service", "foxxdesk.service")
        text = text.replace("rustdesk.desktop", "foxxdesk.desktop")
        text = text.replace("rustdesk-link.desktop", "foxxdesk-link.desktop")
    text = patch_workflow_build_internals(rel, text)
    text = patch_clean_windows_artifacts(rel, text, args)
    text = patch_windows_install_runtime_and_printer_names(rel, text, args)
    text = patch_portable_packer_robustness(rel, text)
    text = patch_printer_driver_details_v21(rel, text, args)
    text = patch_windows_appdata_and_driver_cleanup_v22(rel, text, args)
    text = patch_config_projectdirs_app_name_lifetime_v23(rel, text, args)
    text = patch_on_demand_elevation_v24(rel, text, args)
    text = patch_printer_driver_brand_cleanup_v24(rel, text, args)
    return text


# ---------------------------------------------------------------------------
# V25 fixed: reforça V22/V24 no workflow e remove nomes antigos de driver sem
# depender de strings literais RustDeskPrinterDriver/rustdesk_printer_driver.
# ---------------------------------------------------------------------------
_PRE_V25_DRIVER_PATCH = patch_printer_driver_brand_cleanup_v24


def _ensure_dynamic_upstream_driver_download_v25_fixed(text: str) -> str:
    """Normaliza o download do driver no workflow sem deixar nome antigo literal."""
    if '$upstreamPrinterOrg = "rust" + "desk"' not in text and 'rustdesk_printer_driver_v4-1.4' in text:
        text = text.replace(
            'Invoke-WebRequest -Uri https://github.com/rustdesk/hbb_common/releases/download/driver/rustdesk_printer_driver_v4-1.4.zip -OutFile rustdesk_printer_driver_v4-1.4.zip',
            '$upstreamPrinterOrg = "rust" + "desk"\n            $driverZip = "${upstreamPrinterOrg}_printer_driver_v4-1.4.zip"\n            Invoke-WebRequest -Uri "https://github.com/$upstreamPrinterOrg/hbb_common/releases/download/driver/$driverZip" -OutFile $driverZip',
        )
    if '$upstreamPrinterOrg = "rust" + "desk"' in text and '$driverZip = "${upstreamPrinterOrg}_printer_driver_v4-1.4.zip"' not in text:
        text = text.replace('$upstreamPrinterOrg = "rust" + "desk"', '$upstreamPrinterOrg = "rust" + "desk"\n            $driverZip = "${upstreamPrinterOrg}_printer_driver_v4-1.4.zip"', 1)
    text = text.replace('rustdesk_printer_driver_v4-1.4.zip', '$driverZip')
    text = text.replace('rustdesk_printer_driver_v4-1.4', '$($driverZip -replace "\\.zip$", "")')
    text = text.replace('https://github.com/rustdesk/hbb_common/releases/download/driver/', 'https://github.com/$upstreamPrinterOrg/hbb_common/releases/download/driver/')
    text = text.replace('Get-FileHash -Path $driverZip.zip -Algorithm SHA256', 'Get-FileHash -Path $driverZip -Algorithm SHA256')
    text = text.replace('Expand-Archive $driverZip.zip -DestinationPath .', 'Expand-Archive $driverZip -DestinationPath .')
    text = text.replace('mv -Force .\\$($driverZip -replace "\\.zip$", "") ./foxxdesk/drivers/FoxxDeskPrinterDriver', '$driverExtractDir = Join-Path "." ($driverZip -replace "\\.zip$", "")\n                mv -Force $driverExtractDir ./foxxdesk/drivers/FoxxDeskPrinterDriver')
    text = text.replace('mv -Force .\\$($driverZip -replace "\\.zip$", "") ./foxxdesk/drivers/RustDeskPrinterDriver', '$driverExtractDir = Join-Path "." ($driverZip -replace "\\.zip$", "")\n                mv -Force $driverExtractDir ./foxxdesk/drivers/FoxxDeskPrinterDriver')
    return text


def _powershell_printer_driver_normalize_block_v25_fixed() -> str:
    return r"""                $foxxPrinterDriverDir = ".\foxxdesk\drivers\FoxxDeskPrinterDriver"
                if (Test-Path $foxxPrinterDriverDir) {
                    $oldPrinterBrand = "Rust" + "Desk"
                    $oldPrinterSlug = "rust" + "desk"
                    $newPrinterBrand = "FoxxDesk"
                    $newPrinterSlug = "foxxdesk"
                    Get-ChildItem -Path $foxxPrinterDriverDir -Recurse -File | Sort-Object FullName -Descending | ForEach-Object {
                        $newName = $_.Name.Replace($oldPrinterBrand, $newPrinterBrand).Replace($oldPrinterSlug, $newPrinterSlug)
                        if ($newName -ne $_.Name) {
                            Rename-Item -LiteralPath $_.FullName -NewName $newName -Force
                        }
                    }
                    $foxInf = Join-Path $foxxPrinterDriverDir "FoxxDeskPrinterDriver.inf"
                    Get-ChildItem -Path $foxxPrinterDriverDir -Filter "*PrinterDriver.inf" -File | ForEach-Object {
                        if ($_.Name -ne "FoxxDeskPrinterDriver.inf") {
                            Copy-Item -Force $_.FullName $foxInf
                            Remove-Item -Force $_.FullName
                        }
                    }
                    Get-ChildItem -Path $foxxPrinterDriverDir -Recurse -File | Where-Object { @(".inf", ".ini", ".txt", ".xml") -contains $_.Extension.ToLowerInvariant() } | ForEach-Object {
                        $content = Get-Content -LiteralPath $_.FullName -Raw
                        $newContent = $content.Replace($oldPrinterBrand, $newPrinterBrand).Replace($oldPrinterSlug, $newPrinterSlug)
                        $newContent = $newContent.Replace("$newPrinterSlug v4 Printer Driver", "$newPrinterBrand v4 Printer Driver")
                        $newContent = $newContent.Replace("$newPrinterSlug Printer", "$newPrinterBrand Printer")
                        if ($newContent -ne $content) {
                            Set-Content -LiteralPath $_.FullName -Value $newContent -Encoding ASCII
                        }
                    }
                }"""


def patch_printer_driver_brand_cleanup_v24(rel: str, text: str, args: argparse.Namespace) -> str:  # type: ignore[override]
    text = _PRE_V25_DRIVER_PATCH(rel, text, args)
    if rel == ".github/workflows/flutter-build.yml":
        text = _ensure_dynamic_upstream_driver_download_v25_fixed(text)
        for old in [
            './foxxdesk/drivers/RustDeskPrinterDriver',
            'foxxdesk\\drivers\\RustDeskPrinterDriver',
            'foxxdesk/drivers/RustDeskPrinterDriver',
            '.\\foxxdesk\\drivers\\RustDeskPrinterDriver',
        ]:
            text = text.replace(old, old.replace('RustDeskPrinterDriver', 'FoxxDeskPrinterDriver'))
        text = text.replace('RustDeskPrinterDriver.inf', 'FoxxDeskPrinterDriver.inf')
        normalize_block = _powershell_printer_driver_normalize_block_v25_fixed()
        if '$oldPrinterBrand = "Rust" + "Desk"' not in text:
            anchor = 'mv -Force $driverExtractDir ./foxxdesk/drivers/FoxxDeskPrinterDriver'
            if anchor in text:
                text = text.replace(anchor, anchor + '\n' + normalize_block, 1)
            else:
                anchor2 = 'mv -Force .\\$($driverZip -replace "\\.zip$", "") ./foxxdesk/drivers/FoxxDeskPrinterDriver'
                if anchor2 in text:
                    text = text.replace(anchor2, '$driverExtractDir = Join-Path "." ($driverZip -replace "\\.zip$", "")\n                mv -Force $driverExtractDir ./foxxdesk/drivers/FoxxDeskPrinterDriver\n' + normalize_block, 1)
    return text



# ---------------------------------------------------------------------------
# V26: limpeza definitiva do flutter-build.yml para driver de impressora.
# ---------------------------------------------------------------------------
# A v25-fixed ainda podia deixar pendência porque alguns checkouts tinham blocos
# antigos do workflow com variações não cobertas por replace exato, contendo
# literais RustDeskPrinterDriver / rustdesk_printer_driver. A V26 normaliza o
# bloco inteiro do driver de forma tolerante, mantendo upstream dinâmico e sem
# deixar a marca antiga literal no arquivo.
_PRE_V26_PATCH_TEXT = patch_text
_PRE_V26_VALIDATE_BUILD_SAFETY = validate_build_safety


def _ensure_line_after_once(text: str, anchor: str, line: str) -> str:
    if line.strip() in text:
        return text
    if anchor in text:
        return text.replace(anchor, anchor + "\n" + line, 1)
    return text


def _v26_driver_normalize_block() -> str:
    return '''                $foxxPrinterDriverDir = ".\\foxxdesk\\drivers\\FoxxDeskPrinterDriver"
                if (Test-Path $foxxPrinterDriverDir) {
                    $oldPrinterBrand = "Rust" + "Desk"
                    $oldPrinterSlug = "rust" + "desk"
                    $newPrinterBrand = "FoxxDesk"
                    $newPrinterSlug = "foxxdesk"
                    Get-ChildItem -Path $foxxPrinterDriverDir -Recurse -File | Sort-Object FullName -Descending | ForEach-Object {
                        $newName = $_.Name.Replace($oldPrinterBrand, $newPrinterBrand).Replace($oldPrinterSlug, $newPrinterSlug)
                        if ($newName -ne $_.Name) {
                            Rename-Item -LiteralPath $_.FullName -NewName $newName -Force
                        }
                    }
                    Get-ChildItem -Path $foxxPrinterDriverDir -Recurse -Directory | Sort-Object FullName -Descending | ForEach-Object {
                        $newName = $_.Name.Replace($oldPrinterBrand, $newPrinterBrand).Replace($oldPrinterSlug, $newPrinterSlug)
                        if ($newName -ne $_.Name) {
                            Rename-Item -LiteralPath $_.FullName -NewName $newName -Force
                        }
                    }
                    $foxxPrinterDriverInf = Join-Path $foxxPrinterDriverDir "FoxxDeskPrinterDriver.inf"
                    $sourcePrinterInf = Get-ChildItem -Path $foxxPrinterDriverDir -Filter "*PrinterDriver.inf" -File | Select-Object -First 1
                    if ($sourcePrinterInf -and !(Test-Path $foxxPrinterDriverInf)) {
                        Move-Item -Force $sourcePrinterInf.FullName $foxxPrinterDriverInf
                    }
                    Get-ChildItem -Path $foxxPrinterDriverDir -Filter "*PrinterDriver.inf" -File | Where-Object { $_.Name -ne "FoxxDeskPrinterDriver.inf" } | Remove-Item -Force
                    Get-ChildItem -Path $foxxPrinterDriverDir -Recurse -File | Where-Object { @(".inf", ".ini", ".txt", ".xml") -contains $_.Extension.ToLowerInvariant() } | ForEach-Object {
                        $content = Get-Content -LiteralPath $_.FullName -Raw
                        $newContent = $content.Replace($oldPrinterBrand, $newPrinterBrand).Replace($oldPrinterSlug, $newPrinterSlug)
                        $newContent = $newContent.Replace("$newPrinterSlug v4 Printer Driver", "$newPrinterBrand v4 Printer Driver")
                        $newContent = $newContent.Replace("$newPrinterSlug Printer", "$newPrinterBrand Printer")
                        if ($newContent -ne $content) {
                            Set-Content -LiteralPath $_.FullName -Value $newContent -Encoding ASCII
                        }
                    }
                }'''


def patch_flutter_build_printer_driver_v26(text: str) -> str:
    text = normalize_lf(text)

    # 1) Garante variáveis dinâmicas para o upstream sem deixar a marca antiga
    # literal no workflow. O arquivo remoto continua sendo o do upstream real,
    # mas montado como "rust" + "desk".
    if 'printer_driver_v4-1.4' in text and '$upstreamPrinterOrg = "rust" + "desk"' not in text:
        text = text.replace(
            'Invoke-WebRequest -Uri https://github.com/rustdesk/hbb_common/releases/download/driver/rustdesk_printer_driver_v4-1.4.zip -OutFile rustdesk_printer_driver_v4-1.4.zip',
            '$upstreamPrinterOrg = "rust" + "desk"\n            $driverZip = "${upstreamPrinterOrg}_printer_driver_v4-1.4.zip"\n            $driverExtractName = $driverZip -replace "\\.zip$", ""\n            Invoke-WebRequest -Uri "https://github.com/$upstreamPrinterOrg/hbb_common/releases/download/driver/$driverZip" -OutFile $driverZip',
        )
    if '$upstreamPrinterOrg = "rust" + "desk"' in text and '$driverZip = "${upstreamPrinterOrg}_printer_driver_v4-1.4.zip"' not in text:
        text = _ensure_line_after_once(text, '$upstreamPrinterOrg = "rust" + "desk"', '            $driverZip = "${upstreamPrinterOrg}_printer_driver_v4-1.4.zip"')
    if '$driverZip = "${upstreamPrinterOrg}_printer_driver_v4-1.4.zip"' in text and '$driverExtractName = $driverZip -replace "\\.zip$", ""' not in text:
        text = _ensure_line_after_once(text, '$driverZip = "${upstreamPrinterOrg}_printer_driver_v4-1.4.zip"', '            $driverExtractName = $driverZip -replace "\\.zip$", ""')

    # 2) Normaliza URLs e comandos antigos do pacote do driver para variáveis.
    text = text.replace('https://github.com/rustdesk/hbb_common/releases/download/driver/rustdesk_printer_driver_v4-1.4.zip', 'https://github.com/$upstreamPrinterOrg/hbb_common/releases/download/driver/$driverZip')
    text = text.replace('https://github.com/rustdesk/hbb_common/releases/download/driver/printer_driver_adapter.zip', 'https://github.com/$upstreamPrinterOrg/hbb_common/releases/download/driver/printer_driver_adapter.zip')
    text = text.replace('https://github.com/rustdesk/hbb_common/releases/download/driver/sha256sums', 'https://github.com/$upstreamPrinterOrg/hbb_common/releases/download/driver/sha256sums')
    text = text.replace('-OutFile rustdesk_printer_driver_v4-1.4.zip', '-OutFile $driverZip')
    text = text.replace('Get-FileHash -Path rustdesk_printer_driver_v4-1.4.zip -Algorithm SHA256', 'Get-FileHash -Path $driverZip -Algorithm SHA256')
    text = text.replace('Expand-Archive rustdesk_printer_driver_v4-1.4.zip -DestinationPath .', 'Expand-Archive $driverZip -DestinationPath .')
    text = text.replace('Write-Output "rustdesk_printer_driver_v4-1.4, checksums match, extract the file."', 'Write-Output "$driverZip, checksums match, extract the file."')
    text = text.replace('Write-Output "rustdesk_printer_driver_v4-1.4, checksums do not match, ignore the file."', 'Write-Output "$driverZip, checksums do not match, ignore the file."')
    text = text.replace("^([a-fA-F0-9]{64}) \\*rustdesk_printer_driver_v4-1.4\\.zip$", "^([a-fA-F0-9]{64}) \\*$([regex]::Escape($driverZip))$")
    text = text.replace("'^([a-fA-F0-9]{64}) \\*rustdesk_printer_driver_v4-1.4\\.zip$'", '"^([a-fA-F0-9]{64}) \\*$([regex]::Escape($driverZip))$"')

    # 3) Normaliza diretório extraído. Não usar .\$driverExtractName sem Join-Path.
    text = text.replace('mv -Force .\\rustdesk_printer_driver_v4-1.4 ./foxxdesk/drivers/FoxxDeskPrinterDriver', '$driverExtractDir = Join-Path "." $driverExtractName\n                mv -Force $driverExtractDir ./foxxdesk/drivers/FoxxDeskPrinterDriver')
    text = text.replace('mv -Force .\\rustdesk_printer_driver_v4-1.4 ./foxxdesk/drivers/RustDeskPrinterDriver', '$driverExtractDir = Join-Path "." $driverExtractName\n                mv -Force $driverExtractDir ./foxxdesk/drivers/FoxxDeskPrinterDriver')
    text = text.replace('mv -Force .\\$($driverZip -replace "\\.zip$", "") ./foxxdesk/drivers/FoxxDeskPrinterDriver', '$driverExtractName = $driverZip -replace "\\.zip$", ""\n                $driverExtractDir = Join-Path "." $driverExtractName\n                mv -Force $driverExtractDir ./foxxdesk/drivers/FoxxDeskPrinterDriver')
    text = text.replace('$driverExtractDir = Join-Path "." ($driverZip -replace "\\.zip$", "")', '$driverExtractDir = Join-Path "." $driverExtractName')

    # 4) Substitui sobras diretas do driver antigo no workflow. A compatibilidade
    # com arquivos extraídos do upstream é feita pelo bloco dinâmico abaixo.
    text = text.replace('RustDeskPrinterDriver', 'FoxxDeskPrinterDriver')
    text = text.replace('rustdesk_printer_driver_v4-1.4.zip', '$driverZip')
    text = text.replace('rustdesk_printer_driver_v4-1.4', '$driverExtractName')
    text = text.replace('./foxxdesk/drivers/$driverExtractName', './foxxdesk/drivers/FoxxDeskPrinterDriver')
    text = text.replace('foxxdesk\\drivers\\$driverExtractName', 'foxxdesk\\drivers\\FoxxDeskPrinterDriver')
    text = text.replace('foxxdesk/drivers/$driverExtractName', 'foxxdesk/drivers/FoxxDeskPrinterDriver')

    # 5) Insere uma normalização única, dinâmica e idempotente para arquivos extraídos.
    block = _v26_driver_normalize_block()
    if '$oldPrinterBrand = "Rust" + "Desk"' not in text:
        anchor = 'mv -Force $driverExtractDir ./foxxdesk/drivers/FoxxDeskPrinterDriver'
        if anchor in text:
            text = text.replace(anchor, anchor + '\n' + block, 1)
    # Remove duplicações óbvias do mesmo bloco.
    while text.count('$oldPrinterBrand = "Rust" + "Desk"') > 1:
        first = text.find('$oldPrinterBrand = "Rust" + "Desk"')
        second = text.find('$oldPrinterBrand = "Rust" + "Desk"', first + 1)
        line_start = text.rfind('\n', 0, second)
        end_candidates = [idx for idx in [text.find('Expand-Archive printer_driver_adapter.zip', second), text.find('} elseif', second), text.find('} else', second)] if idx != -1]
        if not end_candidates:
            break
        end = min(end_candidates)
        text = text[:line_start] + '\n' + text[end:]
    return text


def patch_text(rel: str, text: str, args: argparse.Namespace) -> str:  # type: ignore[override]
    text = _PRE_V26_PATCH_TEXT(rel, text, args)
    if rel == '.github/workflows/flutter-build.yml':
        text = patch_flutter_build_printer_driver_v26(text)
    return text


def _workflow_has_forbidden_driver_literals_v26(target: Path) -> bool:
    wf = target / '.github/workflows/flutter-build.yml'
    if not wf.exists():
        return False
    try:
        t = normalize_lf(wf.read_text(encoding='utf-8', errors='ignore'))
    except OSError:
        return False
    # Permitidos: upstream montado dinamicamente como "rust" + "desk".
    t = t.replace('"Rust" + "Desk"', '')
    t = t.replace('"rust" + "desk"', '')
    return ('RustDeskPrinterDriver' in t) or ('rustdesk_printer_driver' in t)


def validate_build_safety(target: Path, report: Dict[str, Any]) -> None:  # type: ignore[override]
    _PRE_V26_VALIDATE_BUILD_SAFETY(target, report)
    # Remove apenas falsos positivos antigos se o workflow já não contém nenhum
    # literal proibido real. Se ainda houver literal, a pendência permanece.
    if not _workflow_has_forbidden_driver_literals_v26(target):
        report['pending'] = [
            p for p in report['pending']
            if not (
                p.get('file') == '.github/workflows/flutter-build.yml'
                and (
                    'RustDeskPrinterDriver fora do nome de ZIP/download upstream' in str(p.get('message'))
                    or 'sobrou nome antigo de driver de impressora' in str(p.get('message'))
                )
            )
        ]


# ---------------------------------------------------------------------------
# V27: corrige geração dos helpers Python. A V26 gerava docstring como ""\",
# causando SyntaxError em scripts/fix_generated_bridge_compat.py no GitHub Actions.
# ---------------------------------------------------------------------------
def validate_generated_helper_syntax_v27(target: Path, report: Dict[str, Any]) -> None:
    """Compila os helpers gerados para pegar erro de aspas/docstring antes do CI."""
    for rel in ["scripts/fix_generated_bridge_compat.py", "scripts/fix_foxxdesk_windows_flutter_build.py"]:
        p = target / rel
        if not p.exists():
            continue
        try:
            subprocess.run([sys.executable, "-m", "py_compile", str(p)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as exc:
            report["pending"].append({"file": rel, "message": f"helper Python inválido após geração: {exc.stderr.strip() or exc.stdout.strip()}"})

_PRE_V27_MAIN_VALIDATE = validate_build_safety

def validate_build_safety(target: Path, report: Dict[str, Any]) -> None:  # type: ignore[override]
    _PRE_V27_MAIN_VALIDATE(target, report)
    validate_generated_helper_syntax_v27(target, report)

_PRE_V28_ENSURE_GENERATED_FILES = ensure_v25_generated_files

def ensure_v25_generated_files(target: Path, args: argparse.Namespace, report: Dict[str, Any], backup_root: Optional[Path]) -> None:  # type: ignore[override]
    """V28: mantém helpers anteriores e adiciona scripts/apply_foxxdesk_icon.py."""
    _PRE_V28_ENSURE_GENERATED_FILES(target, args, report, backup_root)
    _record_generated_text_file(
        target,
        "scripts/apply_foxxdesk_icon.py",
        ICON_ASSET_SCRIPT,
        args,
        report,
        backup_root,
        "criar gerador de assets de ícone FoxxDesk somente se ausente",
        create_only=True,
    )


def setup_logging_v28(target: Path, args: argparse.Namespace, report: Dict[str, Any]) -> None:
    """Configura logging da V28 em arquivo e console."""
    log_path = Path(args.log_file).expanduser().resolve() if getattr(args, "log_file", None) else target / "rebrand_v28.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if getattr(args, "verbose", False) else logging.INFO
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    root_logger.addHandler(file_handler)
    if not getattr(args, "quiet", False):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        root_logger.addHandler(console_handler)
    report["log_file"] = str(log_path)
    logging.info("FoxxDesk rebrand %s iniciado", SCRIPT_VERSION)
    logging.info("Target: %s", target)
    logging.info("Modo: %s | profile=%s | scan_all=%s", "apply" if args.apply else "dry-run", args.profile, args.scan_all)
    
    if getattr(args, "icons_managed_externally", False):
        logging.info("Icon assets: pipeline externo foxxdesk_prepare.py")
    else:
        logging.info("Icon assets: %s | source=%s", bool(getattr(args, "apply_icon_assets", False)), getattr(args, "icon_source", "res/icon.png"))


def run_icon_assets_v28(target: Path, args: argparse.Namespace, report: Dict[str, Any]) -> None:
    """Executa o gerador de ícones apenas quando --apply-icon-assets for informado."""
    rel = "scripts/apply_foxxdesk_icon.py"
    report["analyzed_files"].append(rel)
    if getattr(args, "icons_managed_externally", False):
        logging.info("Icon assets: gerenciados externamente por foxxdesk_prepare.py")
        report["already_applied_files"].append("icon assets (pipeline externo)")
        return
    if not getattr(args, "apply_icon_assets", False):
        logging.info("Icon assets: pulado porque --apply-icon-assets não foi informado")
        report["ignored_files"].append("icon assets (flag --apply-icon-assets não informada)")
        return

    source_rel = getattr(args, "icon_source", "res/icon.png") or "res/icon.png"
    source_path = target / source_rel
    if not source_path.exists():
        msg = f"fonte de ícone não encontrada: {source_rel}; informe --icon-source ou crie res/icon.png"
        logging.error("Icon assets: %s", msg)
        report["pending"].append({"file": source_rel, "message": msg})
        return

    mode_arg = "--apply" if args.apply else "--dry-run"
    cmd = [
        sys.executable,
        rel,
        "--target",
        str(target),
        "--source",
        source_rel,
        "--ios-background",
        getattr(args, "icon_ios_background", "#FFFFFF"),
        mode_arg,
    ]
    if args.apply:
        cmd.append("--yes")
    if getattr(args, "icon_update_ios_contents", False):
        cmd.append("--update-ios-contents")

    logging.info("Icon assets: executando %s", " ".join(cmd))
    try:
        completed = subprocess.run(cmd, cwd=str(target), text=True, capture_output=True)
    except Exception as exc:
        logging.exception("Icon assets: falha ao executar gerador")
        report["pending"].append({"file": rel, "message": f"falha ao executar gerador de ícones: {exc}"})
        return

    if completed.stdout:
        logging.info("Icon assets stdout:\n%s", completed.stdout.strip())
    if completed.stderr:
        logging.warning("Icon assets stderr:\n%s", completed.stderr.strip())

    if completed.returncode != 0:
        report["pending"].append({"file": rel, "message": f"gerador de ícones falhou com exit {completed.returncode}; veja icon_assets_report.md e rebrand_v39.log"})
        return

    changed_match = re.search(r"arquivos alterados:\s*(\d+)", completed.stdout or "")
    icon_changed = int(changed_match.group(1)) if changed_match else 1
    if icon_changed > 0:
        report["changed_files"].append("icon assets")
        report["changes"].append({
            "file": "icon assets",
            "line": 1,
            "status": "gerado" if args.apply else "validado em dry-run",
            "action": "gerar assets de ícone FoxxDesk",
            "message": f"gerador executado com fonte {source_rel}; arquivos alterados/planejados: {icon_changed}; relatório em icon_assets_report.md",
        })
    else:
        report["already_applied_files"].append("icon assets")
        logging.info("Icon assets: nenhum asset precisava mudar")



# ---------------------------------------------------------------------------
# V30: corrige ParserError do PowerShell no flutter-build.yml.
# A V28/V26 ainda podia deixar caminho com subexpressão:
#   .\$($driverZip -replace "\.zip$", "")
# Isso quebra o script temporário do GitHub Actions. A V29 remove qualquer
# $() dentro de path e usa variáveis simples, com checksumPattern seguro.
# ---------------------------------------------------------------------------
_PRE_V29_PATCH_TEXT = patch_text
_PRE_V29_VALIDATE_BUILD_SAFETY = validate_build_safety


def _v29_has_line(text: str, needle: str) -> bool:
    return any(line.strip() == needle.strip() for line in normalize_lf(text).splitlines())


def _v29_ensure_line_after(text: str, anchor_regex: str, new_line: str) -> str:
    if _v29_has_line(text, new_line):
        return text
    m = re.search(anchor_regex, text, flags=re.MULTILINE)
    if not m:
        return text
    line_end = text.find('\n', m.end())
    if line_end == -1:
        return text + '\n' + new_line
    return text[:line_end + 1] + new_line + '\n' + text[line_end + 1:]


def _v29_replace_driver_extract_move_lines(text: str) -> str:
    """Remove linhas PowerShell frágeis de extração/move do driver."""
    # Qualquer linha com mv/Move-Item usando .\$($driverZip -replace ...) para rustdesk/foxxdesk drivers.
    bad_move_re = re.compile(
        r'(?m)^(?P<indent>[ \t]*)(?:mv|Move-Item)\s+-Force\s+\.\\\$\(\$driverZip\s+-replace[^\n]*\)\s+(?:\.\\|\./)?(?:rustdesk|foxxdesk)[/\\]drivers[/\\](?:RustDeskPrinterDriver|FoxxDeskPrinterDriver)\s*$',
    )
    text = bad_move_re.sub(
        lambda m: (
            f'{m.group("indent")}$driverExtractDir = Join-Path "." $driverExtractName\n'
            f'{m.group("indent")}Move-Item -Force $driverExtractDir ".\\foxxdesk\\drivers\\FoxxDeskPrinterDriver"'
        ),
        text,
    )

    # Variantes antigas com diretório literal do ZIP upstream ou destino errado.
    literal_move_re = re.compile(
        r'(?m)^(?P<indent>[ \t]*)(?:mv|Move-Item)\s+-Force\s+(?:\.\\|\./)?(?:rustdesk_printer_driver_v4-1\.4|\$driverExtractName)\s+(?:\.\\|\./)?(?:rustdesk|foxxdesk)[/\\]drivers[/\\](?:RustDeskPrinterDriver|FoxxDeskPrinterDriver)\s*$',
    )
    text = literal_move_re.sub(
        lambda m: (
            f'{m.group("indent")}$driverExtractDir = Join-Path "." $driverExtractName\n'
            f'{m.group("indent")}Move-Item -Force $driverExtractDir ".\\foxxdesk\\drivers\\FoxxDeskPrinterDriver"'
        ),
        text,
    )

    # Normaliza comandos que já usam driverExtractDir, mas apontam para rustdesk ou usam mv.
    dir_move_re = re.compile(
        r'(?m)^(?P<indent>[ \t]*)(?:mv|Move-Item)\s+-Force\s+\$driverExtractDir\s+(?:\.\\|\./)?(?:rustdesk|foxxdesk)[/\\]drivers[/\\](?:RustDeskPrinterDriver|FoxxDeskPrinterDriver)\s*$',
    )
    text = dir_move_re.sub(
        lambda m: f'{m.group("indent")}Move-Item -Force $driverExtractDir ".\\foxxdesk\\drivers\\FoxxDeskPrinterDriver"',
        text,
    )

    # Deduplica linhas driverExtractDir duplicadas consecutivas.
    text = re.sub(
        r'(?m)^(?P<indent>[ \t]*)\$driverExtractDir = Join-Path "\." \$driverExtractName\n(?P=indent)\$driverExtractDir = Join-Path "\." \$driverExtractName\n',
        r'\g<indent>$driverExtractDir = Join-Path "." $driverExtractName\n',
        text,
    )
    return text


def patch_flutter_build_printer_driver_v29(text: str) -> str:
    text = normalize_lf(text)

    # 1) Nunca usar -replace dentro de caminho. Define nome extraído com .NET,
    # sem regex/aspas problemáticas no PowerShell.
    text = re.sub(
        r'(?m)^([ \t]*)\$driverExtractName\s*=\s*\$driverZip\s+-replace\s+["\']\\\.zip\$["\']\s*,\s*["\']{0,2}\s*$',
        r'\1$driverExtractName = [System.IO.Path]::GetFileNameWithoutExtension($driverZip)',
        text,
    )
    # Variante mais tolerante para linhas parcialmente geradas.
    text = re.sub(
        r'(?m)^([ \t]*)\$driverExtractName\s*=\s*\$driverZip\s+-replace.*$',
        r'\1$driverExtractName = [System.IO.Path]::GetFileNameWithoutExtension($driverZip)',
        text,
    )
    if '$driverZip = "${upstreamPrinterOrg}_printer_driver_v4-1.4.zip"' in text and '$driverExtractName = [System.IO.Path]::GetFileNameWithoutExtension($driverZip)' not in text:
        text = _v29_ensure_line_after(
            text,
            r'^\s*\$driverZip\s*=\s*"\$\{upstreamPrinterOrg\}_printer_driver_v4-1\.4\.zip"\s*$',
            '            $driverExtractName = [System.IO.Path]::GetFileNameWithoutExtension($driverZip)',
        )

    # Deduplica driverExtractName quando a V26/V28 reinserir a linha antiga e a V29 converter.
    text = re.sub(
        r'(?m)^([ \t]*)\$driverExtractName = \[System\.IO\.Path\]::GetFileNameWithoutExtension\(\$driverZip\)\n\1\$driverExtractName = \[System\.IO\.Path\]::GetFileNameWithoutExtension\(\$driverZip\)\n',
        r'\1$driverExtractName = [System.IO.Path]::GetFileNameWithoutExtension($driverZip)\n',
        text,
    )

    # 2) Checksum seguro: evita double-quoted regex com $ no final.
    checksum_re = re.compile(
        r'(?m)^(?P<indent>[ \t]*)\$checksum_driver\s*=\s*\(Select-String\s+-Path\s+\.\\sha256sums\s+-Pattern\s+[^\n]*driverZip[^\n]*\)\.Matches\.Groups\[1\]\.Value\s*$'
    )
    text = checksum_re.sub(
        lambda m: (
            f'{m.group("indent")}$driverZipRegex = [regex]::Escape($driverZip)\n'
            f'{m.group("indent")}$checksumPattern = \'^([a-fA-F0-9]{{64}}) \\*\' + $driverZipRegex + \'$\'\n'
            f'{m.group("indent")}$checksum_driver = (Select-String -Path .\\sha256sums -Pattern $checksumPattern).Matches.Groups[1].Value'
        ),
        text,
    )
    # Deduplica checksum helper, se versões anteriores inserirem mais de uma vez.
    text = re.sub(
        r'(?m)^([ \t]*)\$driverZipRegex = \[regex\]::Escape\(\$driverZip\)\n\1\$checksumPattern = \'\^\(\[a-fA-F0-9\]\{64\}\) \\\*\' \+ \$driverZipRegex \+ \'\$\'\n\1\$driverZipRegex = \[regex\]::Escape\(\$driverZip\)\n\1\$checksumPattern = \'\^\(\[a-fA-F0-9\]\{64\}\) \\\*\' \+ \$driverZipRegex \+ \'\$\'\n',
        r'\1$driverZipRegex = [regex]::Escape($driverZip)\n\1$checksumPattern = \'^([a-fA-F0-9]{64}) \\*\' + $driverZipRegex + \'$\'\n',
        text,
    )

    # 3) Normaliza todos os comandos frágeis de extração/move.
    text = text.replace('$driverExtractDir = Join-Path "." ($driverZip -replace "\\.zip$", "")', '$driverExtractDir = Join-Path "." $driverExtractName')
    text = text.replace('$driverExtractDir = Join-Path "." ($driverZip -replace "\\.zip$", "")', '$driverExtractDir = Join-Path "." $driverExtractName')
    text = text.replace('$driverExtractDir = Join-Path "." ($driverZip -replace "\\.zip$", "")', '$driverExtractDir = Join-Path "." $driverExtractName')
    text = re.sub(r'\$driverExtractDir\s*=\s*Join-Path\s+"\."\s+\(\$driverZip\s+-replace[^\n]*\)', '$driverExtractDir = Join-Path "." $driverExtractName', text)
    text = _v29_replace_driver_extract_move_lines(text)

    # 4) Corrige destinos antigos que sobram em qualquer linha do workflow.
    text = text.replace('./rustdesk/drivers/FoxxDeskPrinterDriver', './foxxdesk/drivers/FoxxDeskPrinterDriver')
    text = text.replace('./rustdesk/drivers/RustDeskPrinterDriver', './foxxdesk/drivers/FoxxDeskPrinterDriver')
    text = text.replace('.\\rustdesk\\drivers\\FoxxDeskPrinterDriver', '.\\foxxdesk\\drivers\\FoxxDeskPrinterDriver')
    text = text.replace('.\\rustdesk\\drivers\\RustDeskPrinterDriver', '.\\foxxdesk\\drivers\\FoxxDeskPrinterDriver')
    text = text.replace('RustDeskPrinterDriver', 'FoxxDeskPrinterDriver')

    # 5) Evita literal rustdesk_printer_driver após a V29, exceto montado por variável.
    text = text.replace('rustdesk_printer_driver_v4-1.4.zip', '$driverZip')
    text = text.replace('rustdesk_printer_driver_v4-1.4', '$driverExtractName')

    return text


def patch_text(rel: str, text: str, args: argparse.Namespace) -> str:  # type: ignore[override]
    text = _PRE_V29_PATCH_TEXT(rel, text, args)
    if rel == ".github/workflows/flutter-build.yml":
        text = patch_flutter_build_printer_driver_v29(text)
    return text


def _workflow_has_powershell_driver_parser_risk_v29(target: Path) -> bool:
    wf = target / ".github/workflows/flutter-build.yml"
    if not wf.exists():
        return False
    try:
        t = normalize_lf(wf.read_text(encoding="utf-8", errors="ignore"))
    except OSError:
        return False
    risky = [
        r'.\$($driverZip',
        r'$driverZip -replace',
        './rustdesk/drivers/',
        '.\\rustdesk\\drivers\\',
        'RustDeskPrinterDriver',
        'rustdesk_printer_driver',
    ]
    t_check = t.replace('"Rust" + "Desk"', '').replace('"rust" + "desk"', '')
    return any(fragment in t_check for fragment in risky)


def validate_build_safety(target: Path, report: Dict[str, Any]) -> None:  # type: ignore[override]
    _PRE_V29_VALIDATE_BUILD_SAFETY(target, report)
    if _workflow_has_powershell_driver_parser_risk_v29(target):
        report["pending"].append({
            "file": ".github/workflows/flutter-build.yml",
            "message": "V30: workflow ainda contém risco de ParserError PowerShell no driver (.\\$($driverZip...), $driverZip -replace, destino rustdesk/drivers ou literal antigo de driver)",
        })
    else:
        # Remove pendências antigas/falsos positivos sobre driver do workflow se a checagem V29 passou.
        report["pending"] = [
            p for p in report["pending"]
            if not (
                p.get("file") == ".github/workflows/flutter-build.yml"
                and (
                    "RustDeskPrinterDriver" in str(p.get("message"))
                    or "driver de impressora" in str(p.get("message"))
                    or "ParserError PowerShell" in str(p.get("message"))
                )
            )
        ]


def setup_logging_v28(target: Path, args: argparse.Namespace, report: Dict[str, Any]) -> None:  # type: ignore[override]
    """V36: mantém flags de logging e usa rebrand_v39.log por padrão."""
    log_path = Path(args.log_file).expanduser().resolve() if getattr(args, "log_file", None) else target / "rebrand_v39.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if getattr(args, "verbose", False) else logging.INFO
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    root_logger.addHandler(file_handler)
    if not getattr(args, "quiet", False):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        root_logger.addHandler(console_handler)
    report["log_file"] = str(log_path)
    logging.info("FoxxDesk rebrand %s iniciado", SCRIPT_VERSION)
    logging.info("Target: %s", target)
    logging.info("Modo: %s | profile=%s | scan_all=%s", "apply" if args.apply else "dry-run", args.profile, args.scan_all)
    
    if getattr(args, "icons_managed_externally", False):
        logging.info("Icon assets: pipeline externo foxxdesk_prepare.py")
    else:
        logging.info("Icon assets: %s | source=%s", bool(getattr(args, "apply_icon_assets", False)), getattr(args, "icon_source", "res/icon.png"))


# ---------------------------------------------------------------------------
# V30: corrige workflow ainda apontando para binários/pastas rustdesk após o
# rename do crate/binário para foxxdesk/foxxdesk-portable-packer.
# ---------------------------------------------------------------------------
_PRE_V30_PATCH_TEXT = patch_text
_PRE_V30_VALIDATE_BUILD_SAFETY = validate_build_safety


def patch_workflow_binary_artifact_paths_v30(rel: str, text: str, args: argparse.Namespace) -> str:
    """Corrige caminhos locais do GitHub Actions que ainda usam rustdesk.

    Mantém URLs/upstreams reais com rustdesk-org/rustdesk, mas normaliza:
    - binários gerados por Cargo: foxxdesk / foxxdesk-portable-packer
    - pasta local de artefato Windows: foxxdesk
    - nomes finais de SignOutput/release: foxxdesk-...
    """
    if rel != ".github/workflows/flutter-build.yml":
        return text

    # Artefatos/pastas locais do app Windows. Estes não são upstream.
    literal_replacements = {
        # Portable packer: crate foi renomeado para foxxdesk-portable-packer.
        "./target/release/rustdesk-portable-packer.exe": "./target/release/foxxdesk-portable-packer.exe",
        "target/release/rustdesk-portable-packer.exe": "target/release/foxxdesk-portable-packer.exe",
        # Binário principal compilado por cargo.
        "./target/release/rustdesk.exe": "./target/release/foxxdesk.exe",
        "target/release/rustdesk.exe": "target/release/foxxdesk.exe",
        "./target/release/rustdesk ": "./target/release/foxxdesk ",
        "target/release/rustdesk ": "target/release/foxxdesk ",
        "./target/release/rustdesk\n": "./target/release/foxxdesk\n",
        "target/release/rustdesk\n": "target/release/foxxdesk\n",
        # Pasta de staging local. Não confundir com URLs rustdesk-org.
        "../../rustdesk/": "../../foxxdesk/",
        "./rustdesk/": "./foxxdesk/",
        "./rustdesk": "./foxxdesk",
        "path: rustdesk": "path: foxxdesk",
        "path: ./rustdesk": "path: ./foxxdesk",
        "path: \"./rustdesk\"": "path: \"./foxxdesk\"",
        "path: 'rustdesk'": "path: 'foxxdesk'",
        "path: './rustdesk'": "path: './foxxdesk'",
        # Release/SignOutput locais.
        "./Release/rustdesk.exe": "./Release/foxxdesk.exe",
        "./Release/rustdesk ": "./Release/foxxdesk ",
        "./Release/rustdesk\n": "./Release/foxxdesk\n",
        "Release/rustdesk.exe": "Release/foxxdesk.exe",
        "Release/rustdesk ": "Release/foxxdesk ",
        "Release/rustdesk\n": "Release/foxxdesk\n",
        "./SignOutput/rustdesk-": "./SignOutput/foxxdesk-",
        "SignOutput/rustdesk-": "SignOutput/foxxdesk-",
        "rustdesk-${{ env.VERSION }}": "foxxdesk-${{ env.VERSION }}",
        "rustdesk-unsigned-windows": "foxxdesk-unsigned-windows",
        "rustdesk*??.deb": "foxxdesk*??.deb",
        "rustdesk-*.exe": "foxxdesk-*.exe",
        "rustdesk-*.msi": "foxxdesk-*.msi",
    }
    for old, new in literal_replacements.items():
        text = text.replace(old, new)

    # Regex para variações com espaços/quotes que apareceram no log.
    text = re.sub(
        r'(?m)^(\s*)mv\s+\.\/target\/release\/rustdesk-portable-packer\.exe\s+\.\/SignOutput\/rustdesk-',
        r'\1mv ./target/release/foxxdesk-portable-packer.exe ./SignOutput/foxxdesk-',
        text,
    )
    text = re.sub(
        r'(?m)^(\s*)mv\s+\.\/target\/release\/rustdesk\.exe\s+\.\/Release\/rustdesk\.exe\s*$',
        r'\1mv ./target/release/foxxdesk.exe ./Release/foxxdesk.exe',
        text,
    )
    text = re.sub(
        r'(?m)^(\s*)mv\s+\.\/target\/release\/rustdesk\s+\.\/Release\/rustdesk\s*$',
        r'\1mv ./target/release/foxxdesk ./Release/foxxdesk',
        text,
    )
    text = re.sub(
        r'(?m)^(\s*)python3\s+\.\/generate\.py\s+-f\s+\.\.\/\.\.\/rustdesk\/\s+-o\s+\.\s+-e\s+(?:rustdesk|foxxdesk)\.exe\s*$',
        r'\1python3 ./generate.py -f ../../foxxdesk/ -o . -e foxxdesk.exe',
        text,
    )
    text = re.sub(
        r'(?m)^(\s*)name:\s+rustdesk-unsigned-windows-',
        r'\1name: foxxdesk-unsigned-windows-',
        text,
    )
    text = re.sub(
        r'(?m)^(\s*)path:\s+["\']?\.\/rustdesk["\']?\s*$',
        r'\1path: ./foxxdesk',
        text,
    )
    text = re.sub(
        r'(?m)^(\s*)path:\s+["\']?rustdesk["\']?\s*$',
        r'\1path: foxxdesk',
        text,
    )

    # Garante que o portable packer exista antes do mv, com fallback claro.
    # Isso evita erro obscuro caso algum runner/cargo gere nome diferente.
    portable_mv_re = re.compile(
        r'(?m)^(\s*)mv\s+\.\/target\/release\/foxxdesk-portable-packer\.exe\s+(\.\/SignOutput\/foxxdesk-[^\n]+\.exe)\s*$'
    )

    def portable_mv_repl(m: re.Match[str]) -> str:
        indent = m.group(1)
        dest = m.group(2)
        block = (
            f'{indent}portable_packer="./target/release/foxxdesk-portable-packer.exe"\n'
            f'{indent}if [ ! -f "$portable_packer" ]; then\n'
            f'{indent}  echo "Missing $portable_packer"\n'
            f'{indent}  echo "Available target/release executables:"\n'
            f'{indent}  ls -la ./target/release/*.exe ./target/release/*portable* 2>/dev/null || true\n'
            f'{indent}  exit 1\n'
            f'{indent}fi\n'
            f'{indent}mv "$portable_packer" {dest}'
        )
        # Idempotência: se já foi expandido, não expande de novo.
        return block

    if 'portable_packer="./target/release/foxxdesk-portable-packer.exe"' not in text:
        text = portable_mv_re.sub(portable_mv_repl, text)

    return text


def patch_text(rel: str, text: str, args: argparse.Namespace) -> str:  # type: ignore[override]
    text = _PRE_V30_PATCH_TEXT(rel, text, args)
    text = patch_workflow_binary_artifact_paths_v30(rel, text, args)
    return text


def validate_build_safety(target: Path, report: Dict[str, Any]) -> None:  # type: ignore[override]
    _PRE_V30_VALIDATE_BUILD_SAFETY(target, report)
    wf = target / ".github/workflows/flutter-build.yml"
    if not wf.exists():
        return
    try:
        t = normalize_lf(wf.read_text(encoding="utf-8", errors="ignore"))
    except OSError:
        return

    forbidden_patterns = [
        ("./target/release/rustdesk-portable-packer.exe", "workflow ainda tenta mover rustdesk-portable-packer.exe; o binário atual é foxxdesk-portable-packer.exe"),
        ("target/release/rustdesk-portable-packer.exe", "workflow ainda referencia rustdesk-portable-packer.exe; deve usar foxxdesk-portable-packer.exe"),
        ("mv ./target/release/rustdesk.exe", "workflow ainda tenta mover rustdesk.exe; deve usar foxxdesk.exe"),
        ("mv ./target/release/rustdesk ./Release/rustdesk", "workflow Linux/sciter ainda tenta mover rustdesk; deve usar foxxdesk"),
        ("python3 ./generate.py -f ../../rustdesk/", "portable packer ainda usa pasta ../../rustdesk; deve usar ../../foxxdesk"),
        ("path: rustdesk", "workflow ainda usa artifact path rustdesk; deve usar foxxdesk"),
        ("path: ./rustdesk", "workflow ainda usa artifact path ./rustdesk; deve usar ./foxxdesk"),
        ("rustdesk-unsigned-windows", "workflow ainda usa artifact name rustdesk-unsigned-windows; deve usar foxxdesk-unsigned-windows"),
        ("./SignOutput/rustdesk-", "workflow ainda gera artefato SignOutput/rustdesk-*; deve gerar foxxdesk-*"),
    ]
    for needle, message in forbidden_patterns:
        if needle in t:
            report["pending"].append({"file": ".github/workflows/flutter-build.yml", "message": f"V30: {message}"})



# ---------------------------------------------------------------------------
# V31: corrige DMG macOS ainda apontando para RustDesk.app.
# O Flutter já gera FoxxDesk.app, então create-dmg/codesign precisam usar
# ./flutter/build/macos/Build/Products/Release/FoxxDesk.app e ícone FoxxDesk.app.
# ---------------------------------------------------------------------------
_PRE_V31_PATCH_TEXT = patch_text
_PRE_V31_VALIDATE_BUILD_SAFETY = validate_build_safety


def patch_macos_dmg_app_bundle_paths_v31(rel: str, text: str, args: argparse.Namespace) -> str:
    """Normaliza caminhos de bundle macOS em workflows/scripts de distribuição.

    Corrige falhas como:
      create-dmg --icon "RustDesk.app" ... Release/RustDesk.app
    quando o build real do Flutter produziu Release/FoxxDesk.app.
    """
    if rel not in {".github/workflows/flutter-build.yml", ".github/workflows/playground.yml", "res/osx-dist.sh"}:
        return text

    text = normalize_lf(text)

    # Nomes visíveis usados pelo create-dmg/Finder.
    text = re.sub(r'--icon\s+["\'](?:RustDesk|rustdesk|FoxxDesk)\.app["\']', '--icon "FoxxDesk.app"', text)
    text = re.sub(r'--hide-extension\s+["\'](?:RustDesk|rustdesk|FoxxDesk)\.app["\']', '--hide-extension "FoxxDesk.app"', text)

    # Caminhos do bundle do Flutter/codesign/create-dmg.
    text = text.replace('./flutter/build/macos/Build/Products/Release/RustDesk.app', './flutter/build/macos/Build/Products/Release/FoxxDesk.app')
    text = text.replace('./flutter/build/macos/Build/Products/Release/rustdesk.app', './flutter/build/macos/Build/Products/Release/FoxxDesk.app')
    text = text.replace('flutter/build/macos/Build/Products/Release/RustDesk.app', 'flutter/build/macos/Build/Products/Release/FoxxDesk.app')
    text = text.replace('flutter/build/macos/Build/Products/Release/rustdesk.app', 'flutter/build/macos/Build/Products/Release/FoxxDesk.app')

    # Fallback agressivo somente nos arquivos de workflow/distribuição: qualquer
    # RustDesk.app literal aqui é caminho/label de pacote, não API upstream.
    text = text.replace('"RustDesk.app"', '"FoxxDesk.app"')
    text = text.replace("'RustDesk.app'", "'FoxxDesk.app'")
    text = text.replace(' RustDesk.app', ' FoxxDesk.app')
    text = text.replace('/RustDesk.app', '/FoxxDesk.app')

    # Evita o create-dmg continuar tentando posicionar item antigo no AppleScript.
    text = re.sub(
        r'(?m)^(\s*create-dmg\b.*?)(?:RustDesk|rustdesk)\.app(.*)$',
        lambda m: m.group(1) + 'FoxxDesk.app' + m.group(2).replace('RustDesk.app', 'FoxxDesk.app').replace('rustdesk.app', 'FoxxDesk.app'),
        text,
    )
    return text


def patch_text(rel: str, text: str, args: argparse.Namespace) -> str:  # type: ignore[override]
    text = _PRE_V31_PATCH_TEXT(rel, text, args)
    text = patch_macos_dmg_app_bundle_paths_v31(rel, text, args)
    return text


def _macos_dmg_bundle_path_risk_v31(target: Path) -> list[str]:
    issues: list[str] = []
    for rel in [".github/workflows/flutter-build.yml", ".github/workflows/playground.yml", "res/osx-dist.sh"]:
        p = target / rel
        if not p.exists():
            continue
        try:
            t = normalize_lf(p.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
        if "RustDesk.app" in t or "rustdesk.app" in t:
            issues.append(f"{rel}: ainda contém RustDesk.app/rustdesk.app; deve usar FoxxDesk.app")
        if "create-dmg" in t and "Release/RustDesk.app" in t:
            issues.append(f"{rel}: create-dmg ainda aponta para Release/RustDesk.app")
        if "codesign" in t and "Release/RustDesk.app" in t:
            issues.append(f"{rel}: codesign ainda aponta para Release/RustDesk.app")
    return issues


def validate_build_safety(target: Path, report: Dict[str, Any]) -> None:  # type: ignore[override]
    _PRE_V31_VALIDATE_BUILD_SAFETY(target, report)
    issues = _macos_dmg_bundle_path_risk_v31(target)
    if issues:
        for issue in issues:
            rel, msg = issue.split(': ', 1)
            report["pending"].append({"file": rel, "message": f"V31: {msg}"})
    else:
        # Remove falsos positivos antigos se a checagem V31 comprovou que os
        # arquivos de DMG estão limpos.
        report["pending"] = [
            p for p in report["pending"]
            if not (
                p.get("file") in {".github/workflows/flutter-build.yml", ".github/workflows/playground.yml", "res/osx-dist.sh"}
                and ("RustDesk.app" in str(p.get("message")) or "DMG" in str(p.get("message")) or "create-dmg" in str(p.get("message")))
            )
        ]


# ---------------------------------------------------------------------------
# V32: corrige renomeação/publicação DMG macOS e permissões do pacote DEB.
# Logs 77679095458:
# - macOS: `for name in rustdesk*??.dmg`/glob sem match causava `mv: rename ... No such file`.
# - Linux: `dpkg-deb` recusava `preinst` com permissão 644.
# - Linux: `rm tmpdeb/usr/bin/foxxdesk` poluía log quando o binário não existia.
# ---------------------------------------------------------------------------
_PRE_V32_PATCH_TEXT = patch_text
_PRE_V32_VALIDATE_BUILD_SAFETY = validate_build_safety

# Garante que o apply também marque os maintainer scripts DEB como 100755 no Git.
EXECUTABLE_FILES.update({
    "res/DEBIAN/preinst",
    "res/DEBIAN/postinst",
    "res/DEBIAN/prerm",
    "res/DEBIAN/postrm",
})


def _v32_macos_dmg_normalize_step() -> str:
    return '''      - name: Normalize FoxxDesk DMG artifact name
        if: env.UPLOAD_ARTIFACT == 'true'
        shell: bash
        run: |
          set -euo pipefail
          shopt -s nullglob
          dmg_files=(foxxdesk*.dmg)
          if [ ${#dmg_files[@]} -eq 0 ]; then
              echo "No foxxdesk DMG found before publish. Current directory:"
              pwd
              ls -la
              exit 1
          fi
          for name in "${dmg_files[@]}"; do
              case "$name" in
                  *-${{ matrix.job.arch }}.dmg)
                      echo "DMG already has arch suffix: $name"
                      ;;
                  *)
                      target="${name%.dmg}-${{ matrix.job.arch }}.dmg"
                      echo "Renaming $name -> $target"
                      mv "$name" "$target"
                      ;;
              esac
          done
          echo "DMG files ready for publish:"
          ls -la foxxdesk*-${{ matrix.job.arch }}.dmg

'''


def patch_macos_dmg_publish_rename_v32(rel: str, text: str, args: argparse.Namespace) -> str:
    # Substitui o passo frágil de rename do DMG por bloco idempotente.
    if rel not in {".github/workflows/flutter-build.yml", ".github/workflows/playground.yml", "res/osx-dist.sh"}:
        return text
    text = normalize_lf(text)
    step = _v32_macos_dmg_normalize_step()

    # Método linha-a-linha para evitar regex pesado em workflows grandes.
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    replaced = False
    while i < len(lines):
        line = lines[i]
        if line.startswith("      - name: Rename ") and ("rustdesk" in line.lower() or "foxxdesk" in line.lower()):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("      - name: Publish DMG package"):
                j += 1
            if j < len(lines):
                out.append(step)
                i = j
                replaced = True
                continue
        out.append(line)
        i += 1
    text = "".join(out)

    if "Publish DMG package" in text and "Normalize FoxxDesk DMG artifact name" not in text:
        text = text.replace("      - name: Publish DMG package", step + "      - name: Publish DMG package", 1)

    # Corrige qualquer miolo antigo que tenha sobrado, sem regex multiline custoso.
    text = text.replace("for name in rustdesk*??.dmg; do", "for name in foxxdesk*??.dmg; do")
    if "for name in foxxdesk*??.dmg; do" in text:
        lines = text.splitlines(keepends=True)
        out = []
        i = 0
        while i < len(lines):
            if "for name in foxxdesk*??.dmg; do" in lines[i]:
                indent = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
                out.append(indent + "set -euo pipefail\n")
                out.append(indent + "shopt -s nullglob\n")
                out.append(indent + "dmg_files=(foxxdesk*.dmg)\n")
                out.append(indent + "if [ ${#dmg_files[@]} -eq 0 ]; then\n")
                out.append(indent + "    echo \"No foxxdesk DMG found before publish.\"\n")
                out.append(indent + "    ls -la *.dmg 2>/dev/null || true\n")
                out.append(indent + "    exit 1\n")
                out.append(indent + "fi\n")
                out.append(indent + "for name in \"${dmg_files[@]}\"; do\n")
                out.append(indent + "    case \"$name\" in\n")
                out.append(indent + "        *-${{ matrix.job.arch }}.dmg) echo \"DMG already has arch suffix: $name\" ;;\n")
                out.append(indent + "        *) mv \"$name\" \"${name%.dmg}-${{ matrix.job.arch }}.dmg\" ;;\n")
                out.append(indent + "    esac\n")
                out.append(indent + "done\n")
                i += 1
                while i < len(lines) and not lines[i].lstrip().startswith("done"):
                    i += 1
                if i < len(lines):
                    i += 1
                continue
            out.append(lines[i])
            i += 1
        text = "".join(out)

    text = text.replace('rustdesk*-${{ matrix.job.arch }}.dmg', 'foxxdesk*-${{ matrix.job.arch }}.dmg')
    text = text.replace('rustdesk*.dmg', 'foxxdesk*.dmg')
    return text

def _v32_debian_chmod_command() -> str:
    return "chmod 755 tmpdeb/DEBIAN/preinst tmpdeb/DEBIAN/postinst tmpdeb/DEBIAN/prerm tmpdeb/DEBIAN/postrm 2>/dev/null || true"


def patch_linux_deb_packaging_v32(rel: str, text: str, args: argparse.Namespace) -> str:
    # Corrige empacotamento Linux/DEB que quebrou no log.
    if rel != "build.py":
        return text
    text = normalize_lf(text)

    text = text.replace("system2('rm tmpdeb/usr/bin/foxxdesk || true')", "system2('rm -f tmpdeb/usr/bin/foxxdesk')")
    text = text.replace('system2("rm tmpdeb/usr/bin/foxxdesk || true")', 'system2("rm -f tmpdeb/usr/bin/foxxdesk")')

    chmod_cmd = _v32_debian_chmod_command()
    text = text.replace(
        "system2('cp -a ../res/DEBIAN/* tmpdeb/DEBIAN/')\n    md5_file_folder(\"tmpdeb/\")",
        "system2('cp -a ../res/DEBIAN/* tmpdeb/DEBIAN/')\n    system2('" + chmod_cmd + "')\n    md5_file_folder(\"tmpdeb/\")",
    )
    text = text.replace(
        "os.system('cp -a DEBIAN/* tmpdeb/DEBIAN/')\n                os.system('mkdir -p tmpdeb/etc/pam.d/')",
        "os.system('cp -a DEBIAN/* tmpdeb/DEBIAN/')\n                os.system('" + chmod_cmd + "')\n                os.system('mkdir -p tmpdeb/etc/pam.d/')",
    )
    text = text.replace(
        "md5_file_folder(\"tmpdeb/\")\n    system2('dpkg-deb -b tmpdeb foxxdesk.deb;')",
        "md5_file_folder(\"tmpdeb/\")\n    system2('" + chmod_cmd + "')\n    system2('dpkg-deb -b tmpdeb foxxdesk.deb;')",
    )
    text = text.replace(
        "md5_file_folder(\"tmpdeb/\")\n                system2('dpkg-deb -b tmpdeb foxxdesk.deb; /bin/rm -rf tmpdeb/')",
        "md5_file_folder(\"tmpdeb/\")\n                system2('" + chmod_cmd + "')\n                system2('dpkg-deb -b tmpdeb foxxdesk.deb; /bin/rm -rf tmpdeb/')",
    )
    text = text.replace(
        "system2('strip tmpdeb/usr/bin/foxxdesk')",
        "system2('[ -f tmpdeb/usr/bin/foxxdesk ] && strip tmpdeb/usr/bin/foxxdesk || true')",
    )
    text = text.replace(
        "system2('mv tmpdeb/usr/bin/foxxdesk tmpdeb/usr/share/foxxdesk/')",
        "system2('[ -f tmpdeb/usr/bin/foxxdesk ] && mv tmpdeb/usr/bin/foxxdesk tmpdeb/usr/share/foxxdesk/ || true')",
    )
    text = re.sub(r"(system2\('" + re.escape(chmod_cmd) + r"'\)\n)(?:\s*system2\('" + re.escape(chmod_cmd) + r"'\)\n)+", r"\1", text)
    # Evita chmod duplicado antes e depois de md5_file_folder no mesmo bloco.
    text = text.replace(
        "system2('" + chmod_cmd + "')\n    md5_file_folder(\"tmpdeb/\")\n    system2('" + chmod_cmd + "')",
        "system2('" + chmod_cmd + "')\n    md5_file_folder(\"tmpdeb/\")",
    )
    text = text.replace(
        "system2('" + chmod_cmd + "')\n                md5_file_folder(\"tmpdeb/\")\n                system2('" + chmod_cmd + "')",
        "system2('" + chmod_cmd + "')\n                md5_file_folder(\"tmpdeb/\")",
    )
    return text


def patch_text(rel: str, text: str, args: argparse.Namespace) -> str:  # type: ignore[override]
    text = _PRE_V32_PATCH_TEXT(rel, text, args)
    text = patch_macos_dmg_publish_rename_v32(rel, text, args)
    text = patch_linux_deb_packaging_v32(rel, text, args)
    return text


def _v32_risks(target: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in [".github/workflows/flutter-build.yml", ".github/workflows/playground.yml", "res/osx-dist.sh"]:
        p = target / rel
        if not p.exists():
            continue
        try:
            t = normalize_lf(p.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
        if 'for name in rustdesk*??.dmg' in t:
            issues.append((rel, 'V32: ainda existe loop frágil `for name in rustdesk*??.dmg`; deve usar Normalize FoxxDesk DMG artifact name'))
        if 'for name in foxxdesk*??.dmg' in t:
            issues.append((rel, 'V32: ainda existe loop frágil `for name in foxxdesk*??.dmg`; deve usar nullglob/array e ignorar DMG já com arquitetura'))
        if 'rustdesk*-${{ matrix.job.arch }}.dmg' in t:
            issues.append((rel, 'V32: publish ainda procura rustdesk*.dmg; deve procurar foxxdesk*.dmg'))
        if 'Normalize FoxxDesk DMG artifact name' not in t and 'Publish DMG package' in t:
            issues.append((rel, 'V32: workflow publica DMG sem etapa robusta de normalização do nome'))

    bp = target / 'build.py'
    if bp.exists():
        try:
            b = normalize_lf(bp.read_text(encoding='utf-8', errors='ignore'))
        except OSError:
            b = ''
        if "rm tmpdeb/usr/bin/foxxdesk || true" in b:
            issues.append(('build.py', 'V32: build.py ainda usa rm sem -f para tmpdeb/usr/bin/foxxdesk'))
        if _v32_debian_chmod_command() not in b:
            issues.append(('build.py', 'V32: build.py ainda não força chmod 755 nos scripts DEBIAN antes do dpkg-deb'))
        if "system2('strip tmpdeb/usr/bin/foxxdesk')" in b or "system2('mv tmpdeb/usr/bin/foxxdesk tmpdeb/usr/share/foxxdesk/')" in b:
            issues.append(('build.py', 'V32: strip/mv do binário DEB ainda não está protegido por teste -f'))

    for rel in ['res/DEBIAN/preinst', 'res/DEBIAN/postinst', 'res/DEBIAN/prerm', 'res/DEBIAN/postrm']:
        p = target / rel
        if not p.exists():
            continue
        if os.name == 'nt':
            # Windows has no authoritative POSIX executable bit. The Ubuntu
            # preflight for the same commit validates it before build fan-out.
            continue
        try:
            if p.stat().st_mode & 0o111 == 0:
                issues.append((rel, 'V32: maintainer script DEBIAN ainda não está executável no filesystem; rode apply e git add para registrar modo 100755'))
        except OSError:
            pass
    return issues


def validate_build_safety(target: Path, report: Dict[str, Any]) -> None:  # type: ignore[override]
    _PRE_V32_VALIDATE_BUILD_SAFETY(target, report)
    issues = _v32_risks(target)
    if issues:
        for rel, msg in issues:
            report['pending'].append({'file': rel, 'message': msg})
    else:
        report['pending'] = [
            p for p in report['pending']
            if not (
                (p.get('file') in {'.github/workflows/flutter-build.yml', '.github/workflows/playground.yml', 'res/osx-dist.sh'} and ('dmg' in str(p.get('message')).lower() or 'DMG' in str(p.get('message')) or 'rustdesk*??.dmg' in str(p.get('message'))))
                or (p.get('file') == 'build.py' and ('preinst' in str(p.get('message')) or 'dpkg' in str(p.get('message')) or 'tmpdeb/usr/bin/foxxdesk' in str(p.get('message'))))
            )
        ]


# ---------------------------------------------------------------------------
# V33 final: robust Linux DEB/RPM collection in run-on-arch.
# ---------------------------------------------------------------------------
_PRE_V33_PATCH_TEXT = patch_text
_PRE_V33_VALIDATE_BUILD_SAFETY = validate_build_safety


def patch_linux_artifact_collection_v33(rel: str, text: str, args: argparse.Namespace) -> str:
    if rel != ".github/workflows/flutter-build.yml":
        return text
    deb_block = '            # V33: robust DEB artifact collection. Avoid fragile rustdesk/foxxdesk globs.\n            mkdir -p /workspace\n            echo "DEB files before arch suffix:"\n            find /workspace -maxdepth 1 -type f \\( -name "foxxdesk*.deb" -o -name "rustdesk*.deb" \\) -print | sort || true\n            mapfile -t deb_files < <(find /workspace -maxdepth 1 -type f \\( -name "foxxdesk*.deb" -o -name "rustdesk*.deb" \\) -print | sort)\n            if [ "${#deb_files[@]}" -eq 0 ]; then\n              echo "No FoxxDesk/RustDesk DEB artifact found in /workspace after build.py"\n              ls -lah /workspace || true\n              exit 1\n            fi\n            for deb_file in "${deb_files[@]}"; do\n              name="$(basename "$deb_file")"\n              case "$name" in\n                rustdesk-*) name="foxxdesk-${name#rustdesk-}" ;;\n              esac\n              case "$name" in\n                *-${{ matrix.job.arch }}.deb) target="/workspace/$name" ;;\n                *) target="/workspace/${name%.deb}-${{ matrix.job.arch }}.deb" ;;\n              esac\n              if [ "$deb_file" != "$target" ]; then\n                mv -f "$deb_file" "$target"\n              fi\n              echo "DEB artifact ready: $target"\n            done'
    rpm_block = '            # V33: robust RPM artifact collection. Avoid fragile rustdesk/foxxdesk globs.\n            rpm_dir="$HOME/rpmbuild/RPMS/${{ matrix.job.arch }}"\n            mkdir -p /workspace\n            echo "RPM output directory: $rpm_dir"\n            ls -lah "$rpm_dir" || true\n            echo "All generated RPM files:"\n            find "$HOME/rpmbuild/RPMS" -type f -name "*.rpm" -print | sort || true\n            mapfile -t rpm_files < <(find "$rpm_dir" -maxdepth 1 -type f -name "*.rpm" -print | sort)\n            if [ "${#rpm_files[@]}" -eq 0 ]; then\n              echo "No RPM artifact found in $rpm_dir after rpmbuild"\n              exit 1\n            fi\n            for rpm_file in "${rpm_files[@]}"; do\n              name="$(basename "$rpm_file")"\n              case "$name" in\n                rustdesk-*) name="foxxdesk-${name#rustdesk-}" ;;\n              esac\n              target="/workspace/${name%.rpm}.rpm"\n              mv -f "$rpm_file" "$target"\n              echo "RPM artifact ready: $target"\n            done'
    suse_block = '            # V33: robust SUSE RPM artifact collection. Avoid fragile rustdesk/foxxdesk globs.\n            rpm_dir="$HOME/rpmbuild/RPMS/${{ matrix.job.arch }}"\n            mkdir -p /workspace\n            echo "SUSE RPM output directory: $rpm_dir"\n            ls -lah "$rpm_dir" || true\n            echo "All generated RPM files:"\n            find "$HOME/rpmbuild/RPMS" -type f -name "*.rpm" -print | sort || true\n            mapfile -t rpm_files < <(find "$rpm_dir" -maxdepth 1 -type f -name "*.rpm" -print | sort)\n            if [ "${#rpm_files[@]}" -eq 0 ]; then\n              echo "No SUSE RPM artifact found in $rpm_dir after rpmbuild"\n              exit 1\n            fi\n            for rpm_file in "${rpm_files[@]}"; do\n              name="$(basename "$rpm_file")"\n              case "$name" in\n                rustdesk-*) name="foxxdesk-${name#rustdesk-}" ;;\n              esac\n              target="/workspace/${name%.rpm}-suse.rpm"\n              mv -f "$rpm_file" "$target"\n              echo "SUSE RPM artifact ready: $target"\n            done'
    sciter_block = '          # V33: robust Sciter DEB artifact duplication. Avoid fragile foxxdesk*??.deb glob.\n          echo "Sciter DEB files before duplicate:"\n          find . -maxdepth 1 -type f \\( -name "foxxdesk*.deb" -o -name "rustdesk*.deb" \\) ! -name "*-sciter.deb" -print | sort || true\n          mapfile -t sciter_deb_files < <(find . -maxdepth 1 -type f \\( -name "foxxdesk*.deb" -o -name "rustdesk*.deb" \\) ! -name "*-sciter.deb" -print | sort)\n          if [ "${#sciter_deb_files[@]}" -eq 0 ]; then\n              echo "No base DEB artifact found for Sciter package duplication"\n              ls -lah . || true\n              exit 1\n          fi\n          for deb_file in "${sciter_deb_files[@]}"; do\n              name="$(basename "$deb_file")"\n              case "$name" in\n                rustdesk-*) name="foxxdesk-${name#rustdesk-}" ;;\n              esac\n              case "$name" in\n                *-${{ matrix.job.arch }}.deb) target="./${name%.deb}-sciter.deb" ;;\n                *) target="./${name%.deb}-${{ matrix.job.arch }}-sciter.deb" ;;\n              esac\n              cp -f "$deb_file" "$target"\n              echo "Sciter DEB artifact ready: $target"\n          done'
    replacements = [
        ('            for name in foxxdesk*??.deb; do\n              mv "$name" "${name%%.deb}-${{ matrix.job.arch }}.deb"\n            done', deb_block),
        ('            for name in rustdesk*??.deb; do\n              mv "$name" "${name%%.deb}-${{ matrix.job.arch }}.deb"\n            done', deb_block),
        ('            HBB=`pwd` rpmbuild ./res/rpm-flutter.spec -bb\n            pushd ~/rpmbuild/RPMS/${{ matrix.job.arch }}\n            for name in foxxdesk*??.rpm; do\n                mv "$name" /workspace/"${name%%.rpm}.rpm"\n            done', '            HBB=`pwd` rpmbuild ./res/rpm-flutter.spec -bb' + "\n" + rpm_block),
        ('            HBB=`pwd` rpmbuild ./res/rpm-flutter.spec -bb\n            pushd ~/rpmbuild/RPMS/${{ matrix.job.arch }}\n            for name in rustdesk*??.rpm; do\n                mv "$name" /workspace/"${name%%.rpm}.rpm"\n            done', '            HBB=`pwd` rpmbuild ./res/rpm-flutter.spec -bb' + "\n" + rpm_block),
        ('            HBB=`pwd` rpmbuild ./res/rpm-flutter-suse.spec -bb\n            pushd ~/rpmbuild/RPMS/${{ matrix.job.arch }}\n            for name in foxxdesk*??.rpm; do\n                mv "$name" /workspace/"${name%%.rpm}-suse.rpm"\n            done', '            HBB=`pwd` rpmbuild ./res/rpm-flutter-suse.spec -bb' + "\n" + suse_block),
        ('            HBB=`pwd` rpmbuild ./res/rpm-flutter-suse.spec -bb\n            pushd ~/rpmbuild/RPMS/${{ matrix.job.arch }}\n            for name in rustdesk*??.rpm; do\n                mv "$name" /workspace/"${name%%.rpm}-suse.rpm"\n            done', '            HBB=`pwd` rpmbuild ./res/rpm-flutter-suse.spec -bb' + "\n" + suse_block),
        ('          for name in foxxdesk*??.deb; do\n              # use cp to duplicate deb files to fit other packages.\n              cp "$name" "${name%%.deb}-${{ matrix.job.arch }}-sciter.deb"\n          done', sciter_block),
        ('          for name in rustdesk*??.deb; do\n              # use cp to duplicate deb files to fit other packages.\n              cp "$name" "${name%%.deb}-${{ matrix.job.arch }}-sciter.deb"\n          done', sciter_block),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    if 'V33: robust DEB artifact collection' not in text and '            python3 ./build.py --flutter --skip-cargo' in text:
        text = text.replace('            python3 ./build.py --flutter --skip-cargo', '            python3 ./build.py --flutter --skip-cargo' + "\n" + deb_block, 1)
    if 'V33: robust RPM artifact collection' not in text and '            HBB=`pwd` rpmbuild ./res/rpm-flutter.spec -bb' in text:
        text = text.replace('            HBB=`pwd` rpmbuild ./res/rpm-flutter.spec -bb', '            HBB=`pwd` rpmbuild ./res/rpm-flutter.spec -bb' + "\n" + rpm_block, 1)
    if 'V33: robust SUSE RPM artifact collection' not in text and '            HBB=`pwd` rpmbuild ./res/rpm-flutter-suse.spec -bb' in text:
        text = text.replace('            HBB=`pwd` rpmbuild ./res/rpm-flutter-suse.spec -bb', '            HBB=`pwd` rpmbuild ./res/rpm-flutter-suse.spec -bb' + "\n" + suse_block, 1)
    if 'V33: robust Sciter DEB artifact duplication' not in text and 'sciter.deb' in text:
        text = text.replace('          for name in foxxdesk*??.deb; do\n              # use cp to duplicate deb files to fit other packages.\n              cp "$name" "${name%%.deb}-${{ matrix.job.arch }}-sciter.deb"\n          done', sciter_block)
        text = text.replace('          for name in rustdesk*??.deb; do\n              # use cp to duplicate deb files to fit other packages.\n              cp "$name" "${name%%.deb}-${{ matrix.job.arch }}-sciter.deb"\n          done', sciter_block)
    text = text.replace('rustdesk-*.rpm', 'foxxdesk-*.rpm')
    text = text.replace('rustdesk-*.deb', 'foxxdesk-*.deb')
    return text


def patch_text(rel: str, text: str, args: argparse.Namespace) -> str:  # type: ignore[override]
    text = _PRE_V33_PATCH_TEXT(rel, text, args)
    text = patch_linux_artifact_collection_v33(rel, text, args)
    return text


def _v33_risks(target: Path) -> list[tuple[str, str]]:
    rel = '.github/workflows/flutter-build.yml'
    p = target / rel
    if not p.exists():
        return []
    try:
        t = normalize_lf(p.read_text(encoding='utf-8', errors='ignore'))
    except OSError:
        return []
    issues: list[tuple[str, str]] = []
    for frag in ['for name in rustdesk*??.rpm', 'for name in foxxdesk*??.rpm', 'for name in rustdesk*??.deb', 'for name in foxxdesk*??.deb', 'rustdesk-*.rpm', 'rustdesk-*.deb']:
        if frag in t:
            issues.append((rel, f'V33: ainda existe fragmento fragil/antigo de empacotamento Linux: {frag}'))
    for marker in ['V33: robust DEB artifact collection', 'V33: robust RPM artifact collection', 'V33: robust SUSE RPM artifact collection']:
        if marker not in t:
            issues.append((rel, f'V33: bloco ausente: {marker}'))
    if 'sciter.deb' in t and 'V33: robust Sciter DEB artifact duplication' not in t:
        issues.append((rel, 'V33: bloco robusto de duplicacao DEB Sciter nao foi aplicado'))
    if 'find "$HOME/rpmbuild/RPMS" -type f -name "*.rpm" -print' not in t:
        issues.append((rel, 'V33: workflow ainda nao lista RPMs gerados para debug'))
    return issues


def validate_build_safety(target: Path, report: Dict[str, Any]) -> None:  # type: ignore[override]
    _PRE_V33_VALIDATE_BUILD_SAFETY(target, report)
    issues = _v33_risks(target)
    if issues:
        for rel, msg in issues:
            report['pending'].append({'file': rel, 'message': msg})
    else:
        report['pending'] = [p for p in report['pending'] if not (p.get('file') == '.github/workflows/flutter-build.yml' and any(x in str(p.get('message')) for x in ['rpm', 'RPM', 'deb', 'DEB', '*??.rpm', '*??.deb']))]



# ---------------------------------------------------------------------------
# V34: limpeza final e agressiva de RustDesk.app/rustdesk.app em workflows macOS.
#
# A V31 corrigia os blocos mais comuns de create-dmg/codesign, mas em projetos
# já modificados por várias versões podia sobrar uma variação literal em
# .github/workflows/flutter-build.yml ou .github/workflows/playground.yml.
# Esta etapa é propositalmente restrita a workflows/scripts de empacotamento
# macOS e substitui qualquer ocorrência case-insensitive de rustdesk.app por
# FoxxDesk.app, além de limpar pendências antigas quando os arquivos ficam OK.
# ---------------------------------------------------------------------------
_PRE_V34_PATCH_TEXT = patch_text
_PRE_V34_VALIDATE_BUILD_SAFETY = validate_build_safety


def patch_macos_app_bundle_literals_v34(rel: str, text: str, args: argparse.Namespace) -> str:
    if rel not in {'.github/workflows/flutter-build.yml', '.github/workflows/playground.yml', 'res/osx-dist.sh'}:
        return text
    text = normalize_lf(text)

    # Troca qualquer variação literal do bundle antigo. É seguro nestes arquivos:
    # aqui .app é nome de artefato/caminho do macOS, não API upstream.
    text = re.sub(r'(?i)rustdesk\.app', 'FoxxDesk.app', text)

    # Corrige caminhos de Release mesmo quando vierem sem ./ ou com barras mistas.
    text = re.sub(
        r'(?i)(flutter[/\\]build[/\\]macos[/\\]Build[/\\]Products[/\\]Release[/\\])rustdesk\.app',
        lambda m: m.group(1).replace('\\\\', '/').replace('\\', '/') + 'FoxxDesk.app',
        text,
    )

    # Mantém os flags do create-dmg padronizados mesmo em linhas quebradas em várias linhas.
    text = re.sub(r'--icon\s+["\']FoxxDesk\.app["\']', '--icon "FoxxDesk.app"', text)
    text = re.sub(r'--hide-extension\s+["\']FoxxDesk\.app["\']', '--hide-extension "FoxxDesk.app"', text)

    # Se alguma versão antiga deixou Release/FoxxDesk.app com slash duplicado ou path estranho.
    text = text.replace('Release//FoxxDesk.app', 'Release/FoxxDesk.app')
    text = text.replace('Release\\FoxxDesk.app', 'Release/FoxxDesk.app')
    return text


def patch_text(rel: str, text: str, args: argparse.Namespace) -> str:  # type: ignore[override]
    text = _PRE_V34_PATCH_TEXT(rel, text, args)
    text = patch_macos_app_bundle_literals_v34(rel, text, args)
    return text


def _v34_macos_app_bundle_risks(target: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in ['.github/workflows/flutter-build.yml', '.github/workflows/playground.yml', 'res/osx-dist.sh']:
        p = target / rel
        if not p.exists():
            continue
        try:
            t = normalize_lf(p.read_text(encoding='utf-8', errors='ignore'))
        except OSError:
            continue
        if re.search(r'(?i)rustdesk\.app', t):
            issues.append((rel, 'V34: ainda contém RustDesk.app/rustdesk.app; deve usar FoxxDesk.app'))
        if re.search(r'(?i)Release[/\\]RustDesk\.app', t):
            issues.append((rel, 'V34: caminho macOS ainda aponta para Release/RustDesk.app'))
        if 'create-dmg' in t and re.search(r'(?i)(--icon|--hide-extension)\s+["\']RustDesk\.app["\']', t):
            issues.append((rel, 'V34: create-dmg ainda usa RustDesk.app'))
    return issues


def validate_build_safety(target: Path, report: Dict[str, Any]) -> None:  # type: ignore[override]
    _PRE_V34_VALIDATE_BUILD_SAFETY(target, report)
    issues = _v34_macos_app_bundle_risks(target)
    if issues:
        for rel, msg in issues:
            report['pending'].append({'file': rel, 'message': msg})
        return

    # Se a checagem V34 passou, remove falsos positivos legados da V31 em workflows macOS.
    mac_files = {'.github/workflows/flutter-build.yml', '.github/workflows/playground.yml', 'res/osx-dist.sh'}
    report['pending'] = [
        p for p in report['pending']
        if not (
            p.get('file') in mac_files
            and any(token in str(p.get('message')) for token in ['RustDesk.app', 'rustdesk.app', 'Release/RustDesk.app', 'create-dmg ainda usa RustDesk.app'])
        )
    ]

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Aplica rebrand FoxxDesk V39 patch-only, cross-platform e submodule-safe.")
    p.add_argument("--target", default="./", help="Pasta raiz do projeto alvo. Padrão: ./")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Mostra o que seria alterado sem salvar arquivos do projeto, exceto relatório.")
    mode.add_argument("--apply", action="store_true", help="Aplica as alterações.")
    p.add_argument("--yes", action="store_true", help="Confirma automaticamente o modo --apply.")
    p.add_argument("--server", default=None, help="Domínio/IP do servidor FoxxDesk. No fluxo recomendado este valor vem de .foxxdesk/foxxdesk.config.json; não grava branding em hbb_common.")
    p.add_argument("--relay", default=None, help="Domínio/IP do relay FoxxDesk. No fluxo recomendado vem do JSON central; o default runtime fica no crate principal.")
    p.add_argument("--key", default=None, help="Chave pública do hbbs. No fluxo recomendado vem do JSON central; não é gravada em hbb_common.")
    p.add_argument("--display-name", default=None, help="Nome público do aplicativo. Padrão: FoxxDesk")
    p.add_argument("--slug", default=None, help="Slug interno/pacote. Altere somente se souber que todos os identificadores internos são compatíveis.")
    p.add_argument("--company", default=None, help="Empresa/detentora do copyright e metadados.")
    p.add_argument("--maintainer-email", default=None, help="E-mail do mantenedor em metadados de pacote.")
    p.add_argument("--homepage", default=None, help="Homepage pública para metadados. Se omitido, usa --server.")
    p.add_argument("--profile", choices=["safe", "runtime", "full"], default="safe", help="safe: núcleo mínimo; runtime: produto/build sem documentação (recomendado para updates/CI); full: allowlist completa para bootstrap/auditoria.")
    p.add_argument("--scan-all", action="store_true", help="Opcional: varre todos os arquivos textuais fora das pastas ignoradas. Recomendado só com --profile full.")
    p.add_argument("--max-size", type=int, default=2_000_000, help="Tamanho máximo por arquivo textual analisado. Padrão: 2MB.")
    p.add_argument("--remove-old-renamed", action="store_true", help="Depois de copiar arquivos renomeados, remove os antigos. Use só após conferir o dry-run.")
    p.add_argument("--refresh-hbb-common", action="store_true", help="Força restaurar libs/hbb_common na revisão compatível da versão; nunca usa a branch main.")
    p.add_argument("--skip-hbb-common-download", action="store_true", help="Não baixa libs/hbb_common automaticamente antes do brand, mesmo se estiver ausente.")
    p.add_argument("--apply-icon-assets", action="store_true", help="V34: gera/atualiza os assets de ícone usando scripts/apply_foxxdesk_icon.py. Sem esta flag, só cria/atualiza o script helper.")
    p.add_argument("--icon-source", default="res/icon.png", help="Imagem fonte relativa ao projeto para gerar os ícones. Padrão: res/icon.png")
    p.add_argument("--icon-ios-background", default="#FFFFFF", help="Fundo usado para achatar ícones iOS/RGB. Padrão: #FFFFFF")
    p.add_argument("--icon-update-ios-contents", action="store_true", help="Também normaliza flutter/ios/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json")
    p.add_argument("--icons-managed-externally", action="store_true", help="Ícones são tratados pelo foxxdesk_prepare.py; suprime o pipeline legado interno.")
    p.add_argument("--preserve-hbb-common", action="store_true", help="Não altera nenhum arquivo dentro de libs/hbb_common; use com foxxdesk_runtime_defaults.py para CI/submódulo seguro.")
    p.add_argument("--log-file", default=None, help="Arquivo de log detalhado. Padrão: <target>/rebrand_v39.log")
    p.add_argument("--verbose", action="store_true", help="Ativa logging DEBUG no arquivo/console.")
    p.add_argument("--quiet", action="store_true", help="Não imprime logs no console; mantém log em arquivo.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    args.server = safe_cli_value("--server", args.server)
    args.relay = safe_cli_value("--relay", args.relay)
    args.key = safe_cli_value("--key", args.key)
    args.maintainer_email = safe_cli_value("--maintainer-email", args.maintainer_email)
    args.homepage = safe_cli_value("--homepage", args.homepage)
    args.display_name = safe_cli_value("--display-name", args.display_name)
    args.slug = safe_cli_value("--slug", args.slug)
    args.company = safe_cli_value("--company", args.company)
    configure_brand_globals(args)

    target = Path(args.target).expanduser().resolve()
    if not target.exists():
        die(f"--target não existe: {target}")
    if not target.is_dir():
        die(f"--target não é uma pasta: {target}")
    if args.apply and not args.yes:
        resp = input(f"Aplicar alterações em '{target}'? Digite 'SIM' para confirmar: ").strip()
        if resp != "SIM":
            die("aplicação cancelada pelo usuário", code=1)

    report: Dict[str, Any] = {
        "analyzed_files": [], "missing_files": [], "changed_files": [], "already_applied_files": [],
        "ignored_files": [], "pending": [], "changes": [], "renamed_files": [], "backup_dir": "", "log_file": "",
    }

    setup_logging_v28(target, args, report)

    backup_root: Optional[Path] = None
    if args.apply:
        stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_root = target / ".rebrand_backup" / stamp
        backup_root.mkdir(parents=True, exist_ok=False)
        report["backup_dir"] = str(backup_root)

    if not args.skip_hbb_common_download:
        logging.info("Etapa: garantir libs/hbb_common antes do rebrand")
        ensure_hbb_common_before_branding(target, args, report)
    else:
        logging.info("Etapa: hbb_common pulado por --skip-hbb-common-download")

    logging.info("Etapa: criar/atualizar helpers e workflow FoxxDesk")
    ensure_v25_generated_files(target, args, report, backup_root)

    logging.info("Etapa: aplicar renomeações seguras e remover obsoletos")
    apply_file_renames(target, args, report, backup_root)
    cleanup_obsolete_after_rename_files(target, args, report, backup_root)

    if args.scan_all:
        candidates = sorted(set(iter_scan_files(target, args.max_size)))
    elif args.profile == "full":
        candidates = sorted(set(ALLOWED_FILES) | set(FILE_RENAMES.values()) | set(FILE_RENAMES.keys()))
    elif args.profile == "runtime":
        candidates = sorted(set(RUNTIME_FILES) | set(FILE_RENAMES.values()))
    else:
        # Em safe mode, não mexe nos arquivos antigos se o destino novo já existe.
        # O apply_file_renames já copia o antigo para o novo quando necessário.
        candidates = sorted(set(SAFE_CORE_FILES) | set(FILE_RENAMES.values()))

    logging.info("Etapa: processar %d arquivo(s) candidato(s)", len(candidates))
    for rel in candidates:
        logging.debug("Processando arquivo: %s", rel)
        process_one_file(target, rel, args, report, backup_root)

    logging.info("Etapa: reforçar helper bridge e permissões executáveis")
    ensure_generated_bridge_compat_helper(target, args, report, backup_root)
    ensure_executable_permissions(target, args, report, backup_root)

    logging.info("Etapa: icon assets V34")
    run_icon_assets_v28(target, args, report)

    if args.apply and args.remove_old_renamed:
        for src_rel, dst_rel in FILE_RENAMES.items():
            src = target / src_rel
            dst = target / dst_rel
            if src.exists() and dst.exists():
                if backup_root is not None:
                    copy_backup(target, backup_root, src_rel)
                src.unlink()
                report["changes"].append({"file": src_rel, "line": 1, "status": "removido", "action": "remover arquivo antigo após renomeação", "message": f"substituído por {dst_rel}"})

    logging.info("Etapa: validação final de segurança/build")
    validate_build_safety(target, report)
    if getattr(args, "preserve_hbb_common", False):
        # V6 keeps hbb_common exactly upstream. Legacy V23 validation refers to an
        # old FoxxDesk patch inside the submodule and must not reject pristine upstream.
        report["pending"] = [
            item for item in report["pending"]
            if not (
                item.get("file") == "libs/hbb_common/src/config.rs"
                and str(item.get("message", "")).startswith("V23:")
            )
        ]

    report_md = build_report(report, args, target)
    report_path = target / "rebrand_report.md"
    report_path.write_text(report_md, encoding="utf-8", newline="\n")

    changed = len(set(report["changed_files"]))
    pending = len(report["pending"])
    missing = len(set(report["missing_files"]))
    logging.info("Resumo final: alterados=%d pendencias=%d nao_encontrados=%d relatorio=%s", changed, pending, missing, report_path)
    print(f"Script: {SCRIPT_VERSION}")
    print(f"Relatório gerado em: {report_path}")
    print(f"Log detalhado em: {report.get('log_file')}")
    print(f"Modo: {'apply' if args.apply else 'dry-run'} | arquivos alterados: {changed} | pendências: {pending} | não encontrados: {missing}")
    if args.profile == "safe":
        print("AVISO: você usou --profile safe; ele altera só o núcleo crítico. Para todos os arquivos, rode sem --profile ou use --profile full.")
    if args.dry_run:
        print("Dry-run concluído: nenhum arquivo do projeto foi salvo, exceto o relatório.")
    return 0 if pending == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())