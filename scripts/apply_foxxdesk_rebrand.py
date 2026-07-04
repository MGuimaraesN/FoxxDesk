#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_foxxdesk_rebrand_all_files_no_zip_v24.py

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
import codecs
import datetime as _dt
import hashlib
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

SCRIPT_VERSION = "v24-on-demand-elevation-and-printer-brand-cleanup-2026-07-02"
APP_DISPLAY_NAME = "FoxxDesk"
APP_SLUG = "foxxdesk"
APP_SLUG_UPPER = "FOXXDESK"
DEFAULT_SERVER = "foxxdesk.mguimaraesn.dev"
DEFAULT_KEY = "6WbpsDtYMwUca74qNvNaBfV4pUIGzyXnX1Q8V8fZ8YA="
DEFAULT_MAINTAINER_EMAIL = "mateus@mguimaraesn.dev"

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
    '.gitignore',
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
    'flutter/.gitignore',
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


GENERATED_HELPER_FILES: set[str] = {
    "scripts/fix_generated_bridge_compat.py",
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
}

# Arquivos antigos que não podem coexistir com o novo nome.
# No WiX SDK, todos os .wxs do diretório entram no build; manter RustDesk.wxs
# junto com FoxxDesk.wxs duplica ComponentGroup:Components e Component:App.StartMenu.
OBSOLETE_AFTER_RENAME_FILES: Dict[str, str] = {
    "res/msi/Package/Components/RustDesk.wxs": "res/msi/Package/Components/FoxxDesk.wxs",
}

OPTIONAL_FILES: set[str] = {
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
    ".github/workflows/rustdesk-build.yml": ".github/workflows/foxxdesk-build.yml",
    "flatpak/com.rustdesk.RustDesk.metainfo.xml": "flatpak/com.foxxdesk.client.metainfo.xml",
    "flatpak/rustdesk.json": "flatpak/foxxdesk.json",
    "res/rustdesk-link.desktop": "res/foxxdesk-link.desktop",
    "res/rustdesk.desktop": "res/foxxdesk.desktop",
    "res/rustdesk.service": "res/foxxdesk.service",
    "res/pam.d/rustdesk.debian": "res/pam.d/foxxdesk.debian",
    "res/pam.d/rustdesk.suse": "res/pam.d/foxxdesk.suse",
    "res/msi/Package/Components/RustDesk.wxs": "res/msi/Package/Components/FoxxDesk.wxs",
}

BRIDGE_COMPAT_SCRIPT = r'''#!/usr/bin/env python3
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


def patch_text(rel: str, text: str, args: argparse.Namespace) -> str:
    text = normalize_lf(text)
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
            "action": "remover arquivo antigo que duplica símbolos no MSI",
            "message": f"{old_rel} não pode coexistir com {new_rel}; evita WIX0091/WIX0092",
        })
        if args.apply:
            if backup_root is not None:
                copy_backup(target, backup_root, old_rel)
            try:
                old_path.unlink()
            except OSError as exc:
                report["pending"].append({"file": old_rel, "message": f"falha ao remover arquivo obsoleto: {exc}"})


def ensure_executable_permissions(target: Path, args: argparse.Namespace, report: Dict[str, Any], backup_root: Optional[Path]) -> None:
    '''Marca scripts críticos como executáveis para CI Linux/macOS.

    Importante: o chmod no filesystem precisa ser seguido de `git add` para o
    Git registrar o modo 100755. Isso cobre o caso de
    `flutter/ndk_arm64.sh`, `flutter/build_android_deps.sh` e também `build.py`.
    '''
    for rel in sorted(EXECUTABLE_FILES):
        path = target / rel
        if not path.exists() or not path.is_file():
            # Só marca como ausente o que é realmente obrigatório na raiz.
            # Outros scripts podem não existir em versões/forks diferentes.
            if rel in {"build.py"}:
                report["missing_files"].append(rel)
            continue
        try:
            mode = path.stat().st_mode
        except OSError as exc:
            report["pending"].append({"file": rel, "message": f"falha ao ler permissões: {exc}"})
            continue
        desired = mode | 0o111
        report["analyzed_files"].append(rel)
        if mode == desired:
            report["already_applied_files"].append(rel)
            continue
        report["changed_files"].append(rel)
        report["changes"].append({
            "file": rel,
            "line": 1,
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
        "- Script: `apply_foxxdesk_rebrand_all_files_no_zip_v22.py`",
        f"- Versão do script: `{SCRIPT_VERSION}`",
        "- Payload/ZIP/manifesto externo: `não`",
        "- Espelhamento/substituição de arquivo inteiro por referência antiga: `não`",
        f"- Perfil: `{args.profile}`",
        "- Estratégia: `patch-only; não espelha arquivos inteiros; full = TODOS os arquivos da allowlist + proteção de upstream + fixes Flutter Windows/bridge + portable packer path guard v17 + chmod executável completo + MSI duplicate guard v18 + embedded server/relay/key defaults ocultos + artefatos limpos v20 + ajustes seguros de driver/impressora v21 + AppData Local FoxxDesk e limpeza final de driver v22`",
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

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Aplica rebrand FoxxDesk em todos os arquivos da allowlist, patch-only, sem ZIP/payload/manifesto e sem espelhar arquivos inteiros.")
    p.add_argument("--target", default="./", help="Pasta raiz do projeto alvo. Padrão: ./")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Mostra o que seria alterado sem salvar arquivos do projeto, exceto relatório.")
    mode.add_argument("--apply", action="store_true", help="Aplica as alterações.")
    p.add_argument("--yes", action="store_true", help="Confirma automaticamente o modo --apply.")
    p.add_argument("--server", default=None, help="Domínio/IP do servidor FoxxDesk. Se omitido, usa o DEFAULT_SERVER embutido na v23 e grava defaults ocultos em config.rs.")
    p.add_argument("--relay", default=None, help="Domínio/IP do relay FoxxDesk. Se omitido, usa o mesmo valor do server e grava em config.rs/workflow.")
    p.add_argument("--key", default=None, help="Chave pública do hbbs. Se omitida, usa DEFAULT_KEY e grava em config.rs/workflow.")
    p.add_argument("--maintainer-email", default=None, help="E-mail do mantenedor em metadados de pacote.")
    p.add_argument("--homepage", default=None, help="Homepage pública para metadados. Se omitido, usa --server.")
    p.add_argument("--profile", choices=["safe", "full"], default="full", help="full: TODOS os arquivos da allowlist com rebrand textual patch-only; safe: só correções críticas/build. Padrão: full.")
    p.add_argument("--scan-all", action="store_true", help="Opcional: varre todos os arquivos textuais fora das pastas ignoradas. Recomendado só com --profile full.")
    p.add_argument("--max-size", type=int, default=2_000_000, help="Tamanho máximo por arquivo textual analisado. Padrão: 2MB.")
    p.add_argument("--remove-old-renamed", action="store_true", help="Depois de copiar arquivos renomeados, remove os antigos. Use só após conferir o dry-run.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    args.server = safe_cli_value("--server", args.server)
    args.relay = safe_cli_value("--relay", args.relay)
    args.key = safe_cli_value("--key", args.key)
    args.maintainer_email = safe_cli_value("--maintainer-email", args.maintainer_email)
    args.homepage = safe_cli_value("--homepage", args.homepage)

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
        "ignored_files": [], "pending": [], "changes": [], "renamed_files": [], "backup_dir": "",
    }

    backup_root: Optional[Path] = None
    if args.apply:
        stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_root = target / ".rebrand_backup" / stamp
        backup_root.mkdir(parents=True, exist_ok=False)
        report["backup_dir"] = str(backup_root)

    apply_file_renames(target, args, report, backup_root)
    cleanup_obsolete_after_rename_files(target, args, report, backup_root)

    if args.scan_all:
        candidates = sorted(set(iter_scan_files(target, args.max_size)))
    elif args.profile == "full":
        candidates = sorted(set(ALLOWED_FILES) | set(FILE_RENAMES.values()) | set(FILE_RENAMES.keys()))
    else:
        # Em safe mode, não mexe nos arquivos antigos se o destino novo já existe.
        # O apply_file_renames já copia o antigo para o novo quando necessário.
        candidates = sorted(set(SAFE_CORE_FILES) | set(FILE_RENAMES.values()))

    for rel in candidates:
        process_one_file(target, rel, args, report, backup_root)

    ensure_generated_bridge_compat_helper(target, args, report, backup_root)
    ensure_executable_permissions(target, args, report, backup_root)

    if args.apply and args.remove_old_renamed:
        for src_rel, dst_rel in FILE_RENAMES.items():
            src = target / src_rel
            dst = target / dst_rel
            if src.exists() and dst.exists():
                if backup_root is not None:
                    copy_backup(target, backup_root, src_rel)
                src.unlink()
                report["changes"].append({"file": src_rel, "line": 1, "status": "removido", "action": "remover arquivo antigo após renomeação", "message": f"substituído por {dst_rel}"})

    validate_build_safety(target, report)

    report_md = build_report(report, args, target)
    report_path = target / "rebrand_report.md"
    report_path.write_text(report_md, encoding="utf-8", newline="\n")

    changed = len(set(report["changed_files"]))
    pending = len(report["pending"])
    missing = len(set(report["missing_files"]))
    print(f"Script: {SCRIPT_VERSION}")
    print(f"Relatório gerado em: {report_path}")
    print(f"Modo: {'apply' if args.apply else 'dry-run'} | arquivos alterados: {changed} | pendências: {pending} | não encontrados: {missing}")
    if args.profile == "safe":
        print("AVISO: você usou --profile safe; ele altera só o núcleo crítico. Para todos os arquivos, rode sem --profile ou use --profile full.")
    if args.dry_run:
        print("Dry-run concluído: nenhum arquivo do projeto foi salvo, exceto o relatório.")
    return 0 if pending == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())