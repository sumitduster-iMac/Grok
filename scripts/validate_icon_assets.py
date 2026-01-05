"""
Validate macOS app icon assets.

This repo ships a macOS `.icns` plus an `icon.iconset/` directory.
Launchpad applies its own masking, so the icon images should be full-bleed
and not have transparent edges/corners (otherwise the icon looks "double-masked"
or otherwise visually wrong).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


@dataclass(frozen=True)
class IconPngSpec:
    name: str
    size: int


ICONSET_SPECS: tuple[IconPngSpec, ...] = (
    IconPngSpec("icon_16x16.png", 16),
    IconPngSpec("icon_16x16@2x.png", 32),
    IconPngSpec("icon_32x32.png", 32),
    IconPngSpec("icon_32x32@2x.png", 64),
    IconPngSpec("icon_128x128.png", 128),
    IconPngSpec("icon_128x128@2x.png", 256),
    IconPngSpec("icon_256x256.png", 256),
    IconPngSpec("icon_256x256@2x.png", 512),
    IconPngSpec("icon_512x512.png", 512),
    IconPngSpec("icon_512x512@2x.png", 1024),
)


def _fail(msg: str) -> None:
    raise SystemExit(f"ERROR: {msg}")


def _check_png(path: Path, expected_size: int) -> None:
    if not path.exists():
        _fail(f"Missing iconset file: {path.as_posix()}")

    with Image.open(path) as im:
        if im.size != (expected_size, expected_size):
            _fail(
                f"{path.name} has size {im.size}, expected {(expected_size, expected_size)}"
            )
        # Avoid palette-mode images (they can behave differently in some pipelines).
        if im.mode not in {"RGBA", "RGB"}:
            _fail(f"{path.name} has mode {im.mode}, expected RGBA or RGB")

        # Ensure edges/corners are not transparent.
        if im.mode == "RGBA":
            alpha = im.getchannel("A")
            w, h = im.size
            sample_points = (
                (0, 0),
                (0, h - 1),
                (w - 1, 0),
                (w - 1, h - 1),
                (0, h // 2),
                (w // 2, 0),
                (w - 1, h // 2),
                (w // 2, h - 1),
            )
            for x, y in sample_points:
                a = alpha.getpixel((x, y))
                if a != 255:
                    _fail(
                        f"{path.name} has transparent edge pixel at ({x},{y}) alpha={a}. "
                        "Icons should be full-bleed/opaque at edges for Launchpad."
                    )


def _check_icns(path: Path) -> None:
    if not path.exists():
        _fail(f"Missing .icns file: {path.as_posix()}")

    with Image.open(path) as im:
        if im.format != "ICNS":
            _fail(f"{path.name} is not an ICNS file (format={im.format})")
        # The preview image should also be opaque at edges.
        im = im.convert("RGBA")
        alpha = im.getchannel("A")
        w, h = im.size
        for x, y in ((0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)):
            a = alpha.getpixel((x, y))
            if a != 255:
                _fail(
                    f"{path.name} has transparent corner pixel at ({x},{y}) alpha={a}. "
                    "This usually indicates the icon was pre-masked."
                )


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    logo_dir = repo_root / "macos_grok_overlay" / "logo"
    iconset_dir = logo_dir / "icon.iconset"
    icns_path = logo_dir / "icon.icns"

    if not iconset_dir.exists():
        _fail(f"Missing iconset directory: {iconset_dir.as_posix()}")

    for spec in ICONSET_SPECS:
        _check_png(iconset_dir / spec.name, spec.size)

    _check_icns(icns_path)

    print("OK: icon assets look valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())

