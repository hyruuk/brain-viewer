"""App icon — bundled PNG cropped to content, squared, and circle-masked."""

from __future__ import annotations

from pathlib import Path

from . import config

_SOURCE: Path = Path(__file__).parent / "data" / "icon.png"
_CACHE_VERSION = "v2"
_CACHE: Path = config.CACHE_DIR / f"app_icon_{_CACHE_VERSION}.png"
_OUT_SIZE = 512


def get_app_icon():
    from PySide6 import QtGui

    if not _CACHE.exists():
        try:
            _render_icon(_SOURCE, _CACHE)
        except Exception:
            return QtGui.QIcon(str(_SOURCE)) if _SOURCE.exists() else QtGui.QIcon()
    return QtGui.QIcon(str(_CACHE))


def _render_icon(source: Path, dest: Path) -> None:
    import numpy as np
    from PIL import Image, ImageDraw

    img = Image.open(source).convert("RGBA")

    # Trim transparent padding, ignoring near-zero alpha stray pixels.
    alpha = np.array(img.split()[-1])
    ys, xs = np.where(alpha > 20)
    if xs.size and ys.size:
        img = img.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))

    # Pad to a centered square, oversized so the content fills ~92% of the circle.
    w, h = img.size
    content = max(w, h)
    side = int(content / 0.92)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.paste(img, ((side - w) // 2, (side - h) // 2), img)

    # Resize to final size.
    square = square.resize((_OUT_SIZE, _OUT_SIZE), Image.LANCZOS)

    # Circular alpha mask.
    mask = Image.new("L", (_OUT_SIZE, _OUT_SIZE), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, _OUT_SIZE, _OUT_SIZE), fill=255)
    r, g, b, a = square.split()
    a = Image.eval(a, lambda v: v)  # keep existing transparency
    a = Image.composite(a, Image.new("L", (_OUT_SIZE, _OUT_SIZE), 0), mask)
    out = Image.merge("RGBA", (r, g, b, a))

    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(str(dest))
