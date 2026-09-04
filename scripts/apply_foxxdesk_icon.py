#!/usr/bin/env python3
"""
Generate all FoxxDesk app/logo image assets from a single source: res/icon.png.

v3 scope:
- Root res PNG/SVG/ICO assets.
- Flutter shared asset: flutter/assets/icon.svg.
- Android launcher/status icons under flutter/android/app/src/main/res/mipmap-*.
- Android fastlane store icon.
- iOS AppIcon.appiconset PNGs.
- Windows app_icon.ico.
- macOS AppIcon.icns.

Explicit exclusions:
- res/logo-header.svg
- res/design.svg
- res/icon.png, because it is the source image.

Notes:
- SVG files are SVG wrappers with embedded base64 PNG. They preserve the original dimensions/viewBox,
  but are not true vector traces.
- iOS icons are flattened to RGB because App Store icons must not contain transparency.
- Android notification/status icons are generated as white alpha-mask icons.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import io
import json
import shutil
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps

SCRIPT_VERSION = "icon-assets-v3-all-system-logos-2026-07-01"

try:
    LANCZOS = Image.Resampling.LANCZOS
except AttributeError:  # Pillow < 9
    LANCZOS = Image.LANCZOS

EXCLUDED = {
    "res/logo-header.svg",
    "res/design.svg",
    "res/icon.png",
}

ROOT_PNG_ASSETS = [
    {"path": "res/32x32.png", "size": (32, 32), "mode": "RGBA"},
    {"path": "res/64x64.png", "size": (64, 64), "mode": "RGBA"},
    {"path": "res/128x128.png", "size": (128, 128), "mode": "RGBA"},
    {"path": "res/128x128@2x.png", "size": (256, 256), "mode": "RGBA"},
    {"path": "res/FoxxDesk.png", "size": (1600, 1600), "mode": "RGBA"},
    {"path": "res/mac-icon.png", "size": (1024, 1024), "mode": "RGBA"},
    {"path": "res/mac-tray-dark-x2.png", "size": (60, 60), "mode": "RGBA"},
    {"path": "res/mac-tray-light-x2.png", "size": (48, 48), "mode": "LA"},
    {"path": "fastlane/metadata/android/en-US/images/icon.png", "size": (256, 256), "mode": "RGB"},
]

SVG_ASSETS = [
    {"path": "res/FoxxDesk.svg", "width": 128, "height": 128, "viewBox": "0 0 96 95.999999"},
    {"path": "res/logo.svg", "width": 26, "height": 26, "viewBox": "0 0 96 95.999999"},
    {"path": "res/foxxdesk-banner.svg", "width": 114, "height": 26, "viewBox": "66.993 897.484 113.652 26"},
    {"path": "res/scalable.svg", "width": 32, "height": 32, "viewBox": "66.993 897.484 32 32.000001"},
    {"path": "flutter/assets/icon.svg", "width": 150, "height": 150, "viewBox": "0 0 112.5 112.499997"},
]

ICO_ASSETS = [
    {"path": "res/icon.ico", "render_size": (256, 256), "ico_sizes": [(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)]},
    {"path": "res/tray-icon.ico", "render_size": (32, 32), "ico_sizes": [(16,16), (24,24), (32,32)]},
    {"path": "flutter/windows/runner/resources/app_icon.ico", "render_size": (256, 256), "ico_sizes": [(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)]},
]

ICNS_ASSETS = [
    {"path": "flutter/macos/Runner/AppIcon.icns", "size": (1024, 1024)},
]

ANDROID_DENSITIES = {
    "mdpi": 1.0,
    "hdpi": 1.5,
    "xhdpi": 2.0,
    "xxhdpi": 3.0,
    "xxxhdpi": 4.0,
}

ANDROID_PNG_ASSETS: list[dict[str, Any]] = []
for density, scale in ANDROID_DENSITIES.items():
    folder = f"flutter/android/app/src/main/res/mipmap-{density}"
    launcher = int(round(48 * scale))
    foreground = int(round(108 * scale))
    stat = int(round(24 * scale))
    ANDROID_PNG_ASSETS.extend([
        {"path": f"{folder}/ic_launcher.png", "size": (launcher, launcher), "mode": "RGBA"},
        {"path": f"{folder}/ic_launcher_round.png", "size": (launcher, launcher), "mode": "RGBA", "round_mask": True},
        {"path": f"{folder}/ic_launcher_foreground.png", "size": (foreground, foreground), "mode": "RGBA"},
        {"path": f"{folder}/ic_stat_logo.png", "size": (stat, stat), "mode": "LA"},
    ])

IOS_ICON_SIZES = [
    ("Icon-App-20x20@1x.png", 20),
    ("Icon-App-20x20@2x.png", 40),
    ("Icon-App-20x20@3x.png", 60),
    ("Icon-App-29x29@1x.png", 29),
    ("Icon-App-29x29@2x.png", 58),
    ("Icon-App-29x29@3x.png", 87),
    ("Icon-App-40x40@1x.png", 40),
    ("Icon-App-40x40@2x.png", 80),
    ("Icon-App-40x40@3x.png", 120),
    ("Icon-App-60x60@2x.png", 120),
    ("Icon-App-60x60@3x.png", 180),
    ("Icon-App-76x76@1x.png", 76),
    ("Icon-App-76x76@2x.png", 152),
    ("Icon-App-83.5x83.5@2x.png", 167),
    ("Icon-App-1024x1024@1x.png", 1024),
]

IOS_PNG_ASSETS = [
    {
        "path": f"flutter/ios/Runner/Assets.xcassets/AppIcon.appiconset/{name}",
        "size": (size, size),
        "mode": "RGB",
    }
    for name, size in IOS_ICON_SIZES
]

# A closed manifest of files the script is allowed to generate/update.
ALL_IMAGE_ASSETS: list[dict[str, Any]] = (
    ROOT_PNG_ASSETS
    + ANDROID_PNG_ASSETS
    + IOS_PNG_ASSETS
)

EXPECTED_CONTENTS_JSON_PATH = "flutter/ios/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate all system logo assets from res/icon.png")
    parser.add_argument("--target", default=".", help="Project root. Default: current directory")
    parser.add_argument("--source", default="res/icon.png", help="Source image relative to target. Default: res/icon.png")
    parser.add_argument("--ios-background", default="#FFFFFF", help="Background used when flattening iOS/RGB icons. Default: #FFFFFF")
    parser.add_argument("--update-ios-contents", action="store_true", help="Also normalize iOS AppIcon Contents.json")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Show what would be generated")
    mode.add_argument("--apply", action="store_true", help="Generate/update files")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation in --apply mode")
    return parser.parse_args()


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if len(value) != 6:
        raise ValueError(f"Cor invalida: {value!r}")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def ensure_rgba(im: Image.Image) -> Image.Image:
    return im.convert("RGBA") if im.mode != "RGBA" else im


def square_canvas(src: Image.Image, padding_ratio: float = 0.0) -> Image.Image:
    """Return source centered in a square transparent canvas."""
    src = ensure_rgba(src)
    side = max(src.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.alpha_composite(src, ((side - src.width) // 2, (side - src.height) // 2))
    if padding_ratio <= 0:
        return canvas
    padded_side = round(side / (1 - padding_ratio * 2))
    padded = Image.new("RGBA", (padded_side, padded_side), (0, 0, 0, 0))
    padded.alpha_composite(canvas, ((padded_side - side) // 2, (padded_side - side) // 2))
    return padded


def resize_image(src: Image.Image, size: tuple[int, int]) -> Image.Image:
    return square_canvas(src).resize(size, LANCZOS)


def flatten_to_rgb(im: Image.Image, background: tuple[int, int, int]) -> Image.Image:
    rgba = ensure_rgba(im)
    bg = Image.new("RGBA", rgba.size, (*background, 255))
    bg.alpha_composite(rgba)
    return bg.convert("RGB")


def white_alpha_mask(src: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Create Android/macOS style monochrome icon as white + alpha mask."""
    rgba = resize_image(src, size)
    alpha = rgba.getchannel("A")
    # If source has no useful alpha, derive a mask from luminance.
    if not alpha.getbbox():
        lum = ImageOps.grayscale(rgba.convert("RGB"))
        alpha = ImageOps.invert(lum)
    white = Image.new("L", size, 255)
    return Image.merge("LA", (white, alpha))


def apply_round_mask(im: Image.Image) -> Image.Image:
    rgba = ensure_rgba(im)
    mask = Image.new("L", rgba.size, 0)
    # Pillow ImageDraw imported lazily to keep top imports simple.
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, rgba.width - 1, rgba.height - 1), fill=255)
    rgba.putalpha(Image.composite(rgba.getchannel("A"), Image.new("L", rgba.size, 0), mask))
    return rgba


def png_bytes(src: Image.Image, size: tuple[int, int], mode: str, background: tuple[int, int, int], round_mask: bool = False) -> bytes:
    if mode == "LA":
        out_img = white_alpha_mask(src, size)
    else:
        out_img = resize_image(src, size)
        if round_mask:
            out_img = apply_round_mask(out_img)
        if mode == "RGB":
            out_img = flatten_to_rgb(out_img, background)
        elif mode == "RGBA":
            out_img = ensure_rgba(out_img)
        else:
            out_img = out_img.convert(mode)
    out = io.BytesIO()
    out_img.save(out, format="PNG", optimize=True)
    return out.getvalue()


def parse_viewbox(viewbox: str) -> tuple[float, float, float, float]:
    parts = [float(x) for x in viewbox.replace(",", " ").split()]
    if len(parts) != 4:
        raise ValueError(f"viewBox invalido: {viewbox}")
    return parts[0], parts[1], parts[2], parts[3]


def fmt_num(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.6f}".rstrip("0").rstrip(".")


def svg_bytes(src: Image.Image, width: int, height: int, viewbox: str) -> bytes:
    min_x, min_y, vb_w, vb_h = parse_viewbox(viewbox)
    render_w = max(1, round(vb_w))
    render_h = max(1, round(vb_h))
    png = png_bytes(src, (render_w, render_h), "RGBA", (255, 255, 255))
    b64 = base64.b64encode(png).decode("ascii")
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{width}"
     height="{height}"
     viewBox="{viewbox}"
     version="1.1">
  <image x="{fmt_num(min_x)}"
         y="{fmt_num(min_y)}"
         width="{fmt_num(vb_w)}"
         height="{fmt_num(vb_h)}"
         preserveAspectRatio="xMidYMid meet"
         xlink:href="data:image/png;base64,{b64}" />
</svg>
'''
    return svg.encode("utf-8")


def ico_bytes(src: Image.Image, render_size: tuple[int, int], ico_sizes: list[tuple[int, int]]) -> bytes:
    out = io.BytesIO()
    resize_image(src, render_size).save(out, format="ICO", sizes=ico_sizes)
    return out.getvalue()


def icns_bytes(src: Image.Image, size: tuple[int, int]) -> bytes:
    """Generate macOS .icns. Requires Pillow with ICNS writer support."""
    out = io.BytesIO()
    resize_image(src, size).save(out, format="ICNS")
    return out.getvalue()


def ios_contents_json_bytes() -> bytes:
    images = [
        {"size": "20x20", "idiom": "iphone", "filename": "Icon-App-20x20@2x.png", "scale": "2x"},
        {"size": "20x20", "idiom": "iphone", "filename": "Icon-App-20x20@3x.png", "scale": "3x"},
        {"size": "29x29", "idiom": "iphone", "filename": "Icon-App-29x29@1x.png", "scale": "1x"},
        {"size": "29x29", "idiom": "iphone", "filename": "Icon-App-29x29@2x.png", "scale": "2x"},
        {"size": "29x29", "idiom": "iphone", "filename": "Icon-App-29x29@3x.png", "scale": "3x"},
        {"size": "40x40", "idiom": "iphone", "filename": "Icon-App-40x40@2x.png", "scale": "2x"},
        {"size": "40x40", "idiom": "iphone", "filename": "Icon-App-40x40@3x.png", "scale": "3x"},
        {"size": "60x60", "idiom": "iphone", "filename": "Icon-App-60x60@2x.png", "scale": "2x"},
        {"size": "60x60", "idiom": "iphone", "filename": "Icon-App-60x60@3x.png", "scale": "3x"},
        {"size": "20x20", "idiom": "ipad", "filename": "Icon-App-20x20@1x.png", "scale": "1x"},
        {"size": "20x20", "idiom": "ipad", "filename": "Icon-App-20x20@2x.png", "scale": "2x"},
        {"size": "29x29", "idiom": "ipad", "filename": "Icon-App-29x29@1x.png", "scale": "1x"},
        {"size": "29x29", "idiom": "ipad", "filename": "Icon-App-29x29@2x.png", "scale": "2x"},
        {"size": "40x40", "idiom": "ipad", "filename": "Icon-App-40x40@1x.png", "scale": "1x"},
        {"size": "40x40", "idiom": "ipad", "filename": "Icon-App-40x40@2x.png", "scale": "2x"},
        {"size": "76x76", "idiom": "ipad", "filename": "Icon-App-76x76@1x.png", "scale": "1x"},
        {"size": "76x76", "idiom": "ipad", "filename": "Icon-App-76x76@2x.png", "scale": "2x"},
        {"size": "83.5x83.5", "idiom": "ipad", "filename": "Icon-App-83.5x83.5@2x.png", "scale": "2x"},
        {"size": "1024x1024", "idiom": "ios-marketing", "filename": "Icon-App-1024x1024@1x.png", "scale": "1x"},
    ]
    payload = {"images": images, "info": {"version": 1, "author": "xcode"}}
    return (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def confirm() -> None:
    ans = input("Aplicar geracao de TODOS os assets de logo? [y/N]: ").strip().lower()
    if ans not in {"y", "yes", "s", "sim"}:
        raise SystemExit("Operacao cancelada.")


def backup_file(root: Path, rel: str, backup_root: Path) -> None:
    src = root / rel
    dst = backup_root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def write_if_changed(root: Path, rel: str, data: bytes, dry_run: bool, backup_root: Path, report: list[str]) -> str:
    rel = rel.replace("\\", "/")
    if rel in EXCLUDED:
        report.append(f"- excluido por regra: `{rel}`")
        return "skipped"

    path = root / rel
    existed = path.exists()
    current = path.read_bytes() if existed else None

    if current == data:
        report.append(f"- ja atualizado: `{rel}`")
        return "unchanged"

    if dry_run:
        action = "sera atualizado" if existed else "sera criado"
        report.append(f"- {action}: `{rel}`")
        return "planned"

    if existed:
        backup_file(root, rel, backup_root)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

    if existed:
        report.append(f"- atualizado: `{rel}` (backup em `{backup_root}`)")
    else:
        report.append(f"- criado: `{rel}`")
    return "written"


def generate(root: Path, source_rel: str, dry_run: bool, ios_bg: tuple[int, int, int], update_ios_contents: bool) -> tuple[list[str], dict[str, int], Path]:
    src_path = root / source_rel
    if not src_path.exists():
        raise FileNotFoundError(f"Arquivo fonte nao encontrado: {src_path}")

    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = root / ".icon_asset_backup" / timestamp
    report: list[str] = []
    stats = {"planned": 0, "written": 0, "unchanged": 0, "skipped": 0, "errors": 0}

    with Image.open(src_path) as im:
        src = ensure_rgba(im)

        for item in ALL_IMAGE_ASSETS:
            try:
                data = png_bytes(src, item["size"], item.get("mode", "RGBA"), ios_bg, bool(item.get("round_mask")))
                status = write_if_changed(root, item["path"], data, dry_run, backup_root, report)
                stats[status] += 1
            except Exception as exc:
                report.append(f"- ERRO PNG `{item['path']}`: {exc}")
                stats["errors"] += 1

        for item in SVG_ASSETS:
            try:
                data = svg_bytes(src, item["width"], item["height"], item["viewBox"])
                status = write_if_changed(root, item["path"], data, dry_run, backup_root, report)
                stats[status] += 1
            except Exception as exc:
                report.append(f"- ERRO SVG `{item['path']}`: {exc}")
                stats["errors"] += 1

        for item in ICO_ASSETS:
            try:
                data = ico_bytes(src, item["render_size"], item["ico_sizes"])
                status = write_if_changed(root, item["path"], data, dry_run, backup_root, report)
                stats[status] += 1
            except Exception as exc:
                report.append(f"- ERRO ICO `{item['path']}`: {exc}")
                stats["errors"] += 1

        for item in ICNS_ASSETS:
            try:
                data = icns_bytes(src, item["size"])
                status = write_if_changed(root, item["path"], data, dry_run, backup_root, report)
                stats[status] += 1
            except Exception as exc:
                report.append(f"- ERRO ICNS `{item['path']}`: {exc}")
                stats["errors"] += 1

        if update_ios_contents:
            try:
                data = ios_contents_json_bytes()
                status = write_if_changed(root, EXPECTED_CONTENTS_JSON_PATH, data, dry_run, backup_root, report)
                stats[status] += 1
            except Exception as exc:
                report.append(f"- ERRO JSON `{EXPECTED_CONTENTS_JSON_PATH}`: {exc}")
                stats["errors"] += 1

    return report, stats, backup_root


def main() -> None:
    args = parse_args()
    root = Path(args.target).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Pasta alvo invalida: {root}")

    if args.apply and not args.yes:
        confirm()

    ios_bg = hex_to_rgb(args.ios_background)
    report, stats, backup_root = generate(root, args.source, args.dry_run, ios_bg, args.update_ios_contents)
    mode = "dry-run" if args.dry_run else "apply"
    changed = stats["planned"] if args.dry_run else stats["written"]
    report_path = root / "icon_assets_report.md"

    total_manifest = len(ALL_IMAGE_ASSETS) + len(SVG_ASSETS) + len(ICO_ASSETS) + len(ICNS_ASSETS) + (1 if args.update_ios_contents else 0)
    lines = [
        "# Relatorio de geracao de assets",
        "",
        f"- Script: `{SCRIPT_VERSION}`",
        f"- Modo: `{mode}`",
        f"- Projeto alvo: `{root}`",
        f"- Fonte: `{args.source}`",
        f"- Total no manifesto: `{total_manifest}`",
        f"- Backup: `{backup_root if args.apply and stats['written'] else 'nao criado'}`",
        "",
        "## Regras",
        "",
        "- Fonte unica: `res/icon.png`.",
        "- Nunca altera `res/logo-header.svg`.",
        "- Nunca altera `res/design.svg`.",
        "- Nunca altera `res/icon.png` porque ele e a fonte.",
        "- SVGs sao wrappers com PNG embutido; nao sao vetores reais.",
        "- iOS AppIcon e gerado em RGB sem transparencia.",
        "- Android `ic_stat_logo.png` e gerado como branco + mascara alpha.",
        "",
        "## Resumo",
        "",
        f"- Alteraveis/criados no modo atual: `{changed}`",
        f"- Ja atualizados: `{stats['unchanged']}`",
        f"- Pulados/excluidos: `{stats['skipped']}`",
        f"- Erros: `{stats['errors']}`",
        "",
        "## Arquivos tratados",
        "",
    ]
    lines.extend(report)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Modo: {mode} | arquivos alterados: {changed} | ja atualizados: {stats['unchanged']} | erros: {stats['errors']} | relatorio: {report_path}")


if __name__ == "__main__":
    main()