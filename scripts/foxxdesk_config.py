#!/usr/bin/env python3
"""Central FoxxDesk configuration loader.

All FoxxDesk helpers must read .foxxdesk/foxxdesk.config.json through this
module.  The old .foxxdesk/brand.json is accepted only as a one-way migration
source for empty fields and is never required by CI/builds.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

CONFIG_REL = Path('.foxxdesk/foxxdesk.config.json')
LEGACY_REL = Path('.foxxdesk/brand.json')
SCHEMA_REL = Path('.foxxdesk/foxxdesk.config.schema.json')

DEFAULTS: dict[str, Any] = {
    'version': 4,
    'brand': {
        'display_name': 'FoxxDesk',
        'slug': 'foxxdesk',
        'company': 'MGN Systems',
        'maintainer_name': 'Matheus',
        'maintainer_email': '',
        'homepage': '',
    },
    'network': {
        'server': '',
        'relay': '',
        'key': '',
    },
    'icons': {
        'enabled': True,
        'source': '.foxxdesk/assets/icon.png',
        'fallback_sources': ['res/icon.png', '.foxxdesk/icon-overlay/res/icon.png'],
        'auto_seed_missing_source': True,
        'apply_on_prepare': True,
        'discover_by_name': True,
        'create_brand_owned_assets': True,
        'quality_profile': 'best',
        'min_source_size': 512,
        'recommended_source_size': 1024,
        'padding_ratio': 0.0,
        'ios_background': '#FFFFFF',
        'update_ios_contents': False,
        'png_compress_level': 9,
        'png_optimize': True,
    },
    'rebrand': {
        'profile': 'runtime',
        'ci_profile': 'runtime',
        'bootstrap_profile': 'full',
        'scan_all': False,
        'remove_old_renamed': False,
        'patch_only': True,
        'replace_whole_source_files': False,
        'protect_upstream_names': True,
        'allow_internal_slug_change': False,
    },
    'upstream': {
        'rustdesk_ref': 'auto',
        'sync_hbb_common': True,
        'hbb_common_pins': {
            '1.4.9': '7e1c392c62d39c364127307cd408421dd5f8cfb0',
        },
    },
    'build': {
        'flutter': True,
        'portable': True,
        'hwcodec': True,
        'vram': False,
        'unix_file_copy_paste': True,
        'screencapturekit': True,
        'skip_cargo': False,
        'skip_portable_pack': False,
        'cargo_features': [],
    },
    'github_actions': {
        'enabled': True,
        'validate_before_build': True,
        'install_icon_dependencies': False,
        'deterministic_icon_cache_in_ci': True,
    },
    'safety': {
        'fail_on_missing_required_files': True,
        'fail_on_incompatible_hbb_common': True,
        'backup_before_patch': True,
        'require_nonempty_server': True,
        'require_nonempty_key': True,
        'allow_unverified_icon_fallback': False,
    },
}


def _deep_merge(default: Any, value: Any) -> Any:
    if isinstance(default, dict) and isinstance(value, dict):
        out = copy.deepcopy(default)
        for key, val in value.items():
            out[key] = _deep_merge(default.get(key), val) if key in default else copy.deepcopy(val)
        return out
    return copy.deepcopy(value)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError as exc:
        raise RuntimeError(f'Configuração ausente: {path}') from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f'JSON inválido em {path}: {exc}') from exc
    if not isinstance(data, dict):
        raise RuntimeError(f'Configuração deve ser um objeto JSON: {path}')
    return data


def _migrate_legacy(root: Path, cfg: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    legacy_path = root / LEGACY_REL
    if not legacy_path.is_file():
        return cfg, []
    try:
        legacy = _read_json(legacy_path)
    except Exception:
        return cfg, []
    old_brand = legacy.get('brand', {}) if isinstance(legacy.get('brand'), dict) else {}
    old_upstream = legacy.get('upstream', {}) if isinstance(legacy.get('upstream'), dict) else {}
    changed: list[str] = []

    mappings = [
        (('brand', 'display_name'), old_brand.get('display_name')),
        (('brand', 'slug'), old_brand.get('slug')),
        (('network', 'server'), old_brand.get('server')),
        (('network', 'relay'), old_brand.get('relay')),
        (('network', 'key'), old_brand.get('key')),
        (('icons', 'ios_background'), old_brand.get('ios_background')),
    ]
    for (section, key), old_value in mappings:
        if old_value in (None, ''):
            continue
        current = cfg.setdefault(section, {}).get(key)
        if current in (None, ''):
            cfg[section][key] = old_value
            changed.append(f'{section}.{key}')

    if old_upstream:
        up = cfg.setdefault('upstream', {})
        if not up.get('rustdesk_ref') and old_upstream.get('rustdesk_ref'):
            up['rustdesk_ref'] = old_upstream['rustdesk_ref']
            changed.append('upstream.rustdesk_ref')
        pins = up.setdefault('hbb_common_pins', {})
        for version, sha in (old_upstream.get('hbb_common_pins') or {}).items():
            if version not in pins and sha:
                pins[version] = sha
                changed.append(f'upstream.hbb_common_pins.{version}')
    return cfg, changed


def validate_config(cfg: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    brand = cfg.get('brand', {})
    network = cfg.get('network', {})
    icons = cfg.get('icons', {})
    rebrand = cfg.get('rebrand', {})
    safety = cfg.get('safety', {})

    display = str(brand.get('display_name', '')).strip()
    slug = str(brand.get('slug', '')).strip()
    if not display:
        errors.append('brand.display_name não pode ser vazio')
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', slug):
        errors.append('brand.slug deve usar apenas a-z, 0-9, _ ou - e começar por letra/número')
    if not bool(rebrand.get('allow_internal_slug_change')) and slug != 'foxxdesk':
        errors.append("brand.slug diferente de 'foxxdesk' exige rebrand.allow_internal_slug_change=true")

    server = str(network.get('server', '')).strip()
    key = str(network.get('key', '')).strip()
    if safety.get('require_nonempty_server', True) and not server:
        errors.append('network.server não pode ser vazio')
    if safety.get('require_nonempty_key', True) and not key:
        errors.append('network.key não pode ser vazio')

    if icons.get('enabled', True):
        source = str(icons.get('source', '')).strip()
        if not source:
            errors.append('icons.source não pode ser vazio quando icons.enabled=true')
        if str(icons.get('quality_profile', 'best')) not in {'best', 'balanced', 'fast'}:
            errors.append('icons.quality_profile deve ser best, balanced ou fast')
        try:
            padding = float(icons.get('padding_ratio', 0.0))
            if not 0.0 <= padding < 0.45:
                errors.append('icons.padding_ratio deve ficar entre 0 e 0.45')
        except Exception:
            errors.append('icons.padding_ratio inválido')

    for field in ('profile', 'ci_profile', 'bootstrap_profile'):
        if str(rebrand.get(field, 'safe')) not in {'safe', 'runtime', 'full'}:
            errors.append(f'rebrand.{field} deve ser safe, runtime ou full')
    return errors


def load_config(root: Path, *, migrate_legacy: bool = True, write_migration: bool = False) -> tuple[dict[str, Any], list[str]]:
    path = root / CONFIG_REL
    cfg = _deep_merge(DEFAULTS, _read_json(path))
    migrated: list[str] = []
    if migrate_legacy:
        cfg, migrated = _migrate_legacy(root, cfg)
    cfg['$schema'] = './foxxdesk.config.schema.json'
    cfg['version'] = 4
    if not cfg['network'].get('relay'):
        cfg['network']['relay'] = cfg['network'].get('server', '')
    if not cfg['brand'].get('homepage') and cfg['network'].get('server'):
        cfg['brand']['homepage'] = 'https://' + str(cfg['network']['server']).strip('/')
    errors = validate_config(cfg)
    if errors:
        raise RuntimeError('Configuração FoxxDesk inválida: ' + '; '.join(errors))
    if migrated and write_migration:
        save_config(root, cfg)
    return cfg, migrated


def save_config(root: Path, cfg: dict[str, Any]) -> None:
    path = root / CONFIG_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
