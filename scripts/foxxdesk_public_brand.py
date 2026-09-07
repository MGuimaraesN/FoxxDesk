#!/usr/bin/env python3
"""Apply/check FoxxDesk public platform branding with narrow semantic patches.

This module owns the public-brand invariants that the validator checks:
- Android string app_name
- Android <application android:label>
- macOS PRODUCT_NAME
- Windows ProductName (+ matching executable metadata when those fields exist)
- Linux desktop/link Name and systemd Description

It intentionally does not scan the repository or replace generic RustDesk strings.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional
from xml.sax.saxutils import escape as xml_escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from foxxdesk_config import load_config  # noqa: E402

SCRIPT_VERSION = 'foxxdesk-public-brand-v2-linux-semantic-2026-09-06'


class BrandPatchError(RuntimeError):
    pass


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='ignore')


def write_if_changed(path: Path, before: str, after: str, *, apply: bool) -> bool:
    if before == after:
        return False
    if apply:
        path.write_text(after, encoding='utf-8', newline='\n')
    return True


def xml_string_value(text: str, name: str) -> Optional[str]:
    m = re.search(
        rf'<string\b[^>]*\bname\s*=\s*["\']{re.escape(name)}["\'][^>]*>\s*([^<]+?)\s*</string\s*>',
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return m.group(1).strip() if m else None


def android_application_label(manifest: str) -> Optional[str]:
    m = re.search(r'<application\b([^>]*)>', manifest, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    a = re.search(r'android:label\s*=\s*["\']([^"\']+)["\']', m.group(1), flags=re.IGNORECASE)
    return a.group(1).strip() if a else None


def xcconfig_value(text: str, key: str) -> Optional[str]:
    m = re.search(rf'(?m)^\s*{re.escape(key)}\s*=\s*(.*?)\s*$', text)
    if not m:
        return None
    return m.group(1).strip().strip('"\'')


def rc_string_value(text: str, key: str) -> Optional[str]:
    m = re.search(
        rf'VALUE\s+["\']{re.escape(key)}["\']\s*,\s*["\']([^"\']*)["\']',
        text,
        flags=re.IGNORECASE,
    )
    return m.group(1).rstrip('\\0').strip() if m else None


def patch_android_strings(text: str, display: str) -> str:
    pat = re.compile(
        r'(<string\b[^>]*\bname\s*=\s*["\']app_name["\'][^>]*>)(.*?)(</string\s*>)',
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not pat.search(text):
        raise BrandPatchError('Android strings.xml: <string name="app_name"> não encontrado')
    value = xml_escape(display)
    return pat.sub(lambda m: m.group(1) + value + m.group(3), text, count=1)


def patch_android_manifest(text: str) -> str:
    app = re.search(r'<application\b[^>]*>', text, flags=re.IGNORECASE | re.DOTALL)
    if not app:
        raise BrandPatchError('AndroidManifest.xml: tag <application> não encontrada')
    tag = app.group(0)
    label_pat = re.compile(r'android:label\s*=\s*(["\'])([^"\']*)\1', flags=re.IGNORECASE)
    if label_pat.search(tag):
        new_tag = label_pat.sub('android:label="@string/app_name"', tag, count=1)
    else:
        # Keep the upstream tag structure and add only one attribute before the closing >.
        if tag.rstrip().endswith('/>'):
            new_tag = re.sub(r'/\s*>$', ' android:label="@string/app_name" />', tag, count=1)
        else:
            new_tag = re.sub(r'>$', ' android:label="@string/app_name">', tag, count=1)
    return text[:app.start()] + new_tag + text[app.end():]


def patch_xcconfig(text: str, key: str, value: str, label: str) -> str:
    pat = re.compile(rf'(?m)^(\s*{re.escape(key)}\s*=\s*).*$')
    if not pat.search(text):
        raise BrandPatchError(f'{label}: {key} não encontrado')
    return pat.sub(lambda m: m.group(1) + value, text, count=1)


def rc_escape(value: str) -> str:
    return value.replace('\\', '\\\\').replace('"', '\\"')


def patch_rc_value(text: str, key: str, value: str, *, required: bool) -> str:
    # Preserve the file's suffix style ("\\0" may be outside or inside the value).
    pat = re.compile(
        rf'(VALUE\s+"{re.escape(key)}"\s*,\s*")([^"]*)(")',
        flags=re.IGNORECASE,
    )
    if not pat.search(text):
        if required:
            raise BrandPatchError(f'Runner.rc: campo {key} não encontrado')
        return text
    escaped = rc_escape(value)
    return pat.sub(lambda m: m.group(1) + escaped + m.group(3), text, count=1)


def patch_ini_key(text: str, key: str, value: str, label: str) -> str:
    pat = re.compile(rf'(?m)^(\s*{re.escape(key)}\s*=).*$')
    if not pat.search(text):
        raise BrandPatchError(f'{label}: chave {key} não encontrada')
    return pat.sub(lambda m: m.group(1) + value, text, count=1)


def ini_value(text: str, key: str) -> Optional[str]:
    m = re.search(rf'(?m)^\s*{re.escape(key)}\s*=\s*(.*?)\s*$', text)
    return m.group(1).strip() if m else None


def desired_errors(root: Path, display: str) -> list[str]:
    errors: list[str] = []

    strings_path = root / 'flutter/android/app/src/main/res/values/strings.xml'
    if not strings_path.is_file():
        errors.append(f'arquivo obrigatório ausente: {strings_path.relative_to(root)}')
        strings_value = None
    else:
        strings_value = xml_string_value(read(strings_path), 'app_name')
        if strings_value != display:
            errors.append(f'Android app_name = {strings_value!r}, esperado {display!r}')

    manifest_path = root / 'flutter/android/app/src/main/AndroidManifest.xml'
    if not manifest_path.is_file():
        errors.append(f'arquivo obrigatório ausente: {manifest_path.relative_to(root)}')
    else:
        label = android_application_label(read(manifest_path))
        if label == '@string/app_name':
            if strings_value != display:
                errors.append(f'Android application label usa @string/app_name, mas app_name != {display!r}')
        elif label != display:
            errors.append(f'Android application label = {label!r}, esperado {display!r} ou @string/app_name')

    mac_path = root / 'flutter/macos/Runner/Configs/AppInfo.xcconfig'
    if not mac_path.is_file():
        errors.append(f'arquivo obrigatório ausente: {mac_path.relative_to(root)}')
    else:
        value = xcconfig_value(read(mac_path), 'PRODUCT_NAME')
        if value != display:
            errors.append(f'macOS PRODUCT_NAME = {value!r}, esperado {display!r}')

    win_path = root / 'flutter/windows/runner/Runner.rc'
    if not win_path.is_file():
        errors.append(f'arquivo obrigatório ausente: {win_path.relative_to(root)}')
    else:
        value = rc_string_value(read(win_path), 'ProductName')
        if value != display:
            errors.append(f'Windows ProductName = {value!r}, esperado {display!r}')

    linux_public = [
        ('res/foxxdesk.desktop', 'Name', display),
        ('res/foxxdesk-link.desktop', 'Name', display),
        ('res/foxxdesk.service', 'Description', display),
    ]
    for rel, key, expected in linux_public:
        path = root / rel
        if not path.is_file():
            errors.append(f'arquivo obrigatório ausente: {rel}')
            continue
        value = ini_value(read(path), key)
        if value != expected:
            errors.append(f'{rel}: {key} = {value!r}, esperado {expected!r}')

    return errors


def apply_or_check(root: Path, *, apply: bool) -> int:
    cfg, _ = load_config(root, migrate_legacy=True, write_migration=False)
    brand = cfg['brand']
    display = str(brand['display_name']).strip()
    slug = str(brand.get('slug') or 'foxxdesk').strip()
    if not display:
        raise BrandPatchError('brand.display_name vazio')

    files: list[tuple[Path, str]] = [
        (root / 'flutter/android/app/src/main/res/values/strings.xml', 'android strings'),
        (root / 'flutter/android/app/src/main/AndroidManifest.xml', 'android manifest'),
        (root / 'flutter/macos/Runner/Configs/AppInfo.xcconfig', 'macOS xcconfig'),
        (root / 'flutter/windows/runner/Runner.rc', 'Windows resource'),
        (root / 'res/foxxdesk.desktop', 'Linux desktop'),
        (root / 'res/foxxdesk-link.desktop', 'Linux URL desktop'),
        (root / 'res/foxxdesk.service', 'Linux service'),
    ]
    for path, label in files:
        if not path.is_file():
            raise BrandPatchError(f'{label}: arquivo ausente: {path.relative_to(root)}')

    changed = 0

    path = files[0][0]
    before = read(path)
    after = patch_android_strings(before, display)
    changed += int(write_if_changed(path, before, after, apply=apply))

    path = files[1][0]
    before = read(path)
    after = patch_android_manifest(before)
    changed += int(write_if_changed(path, before, after, apply=apply))

    path = files[2][0]
    before = read(path)
    after = patch_xcconfig(before, 'PRODUCT_NAME', display, 'AppInfo.xcconfig')
    changed += int(write_if_changed(path, before, after, apply=apply))

    path = files[3][0]
    before = read(path)
    after = patch_rc_value(before, 'ProductName', display, required=True)
    after = patch_rc_value(after, 'FileDescription', f'{display} Remote Desktop', required=False)
    after = patch_rc_value(after, 'InternalName', slug, required=False)
    after = patch_rc_value(after, 'OriginalFilename', f'{slug}.exe', required=False)
    changed += int(write_if_changed(path, before, after, apply=apply))

    for path, key, label in [
        (root / 'res/foxxdesk.desktop', 'Name', 'foxxdesk.desktop'),
        (root / 'res/foxxdesk-link.desktop', 'Name', 'foxxdesk-link.desktop'),
        (root / 'res/foxxdesk.service', 'Description', 'foxxdesk.service'),
    ]:
        before = read(path)
        after = patch_ini_key(before, key, display, label)
        changed += int(write_if_changed(path, before, after, apply=apply))

    if apply:
        errors = desired_errors(root, display)
        if errors:
            raise BrandPatchError('pós-validação falhou: ' + '; '.join(errors))
    else:
        errors = desired_errors(root, display)
        if errors:
            raise BrandPatchError('; '.join(errors))

    mode = 'apply' if apply else 'check'
    print(f'FoxxDesk public brand OK: {changed} arquivo(s) alterado(s) ({SCRIPT_VERSION}, {mode})')
    return changed


def main() -> int:
    p = argparse.ArgumentParser(description='Aplica/valida nome público FoxxDesk em Android, macOS, Windows e Linux')
    p.add_argument('--target', default='.')
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = p.parse_args()
    root = Path(args.target).expanduser().resolve()
    try:
        apply_or_check(root, apply=args.apply)
    except Exception as exc:
        print(f'ERRO public brand: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
