"""sigil -- a deterministic avatar for any string.

The name is hashed with SHA-256, the digest's bits become a grid that is
mirrored down the middle (the way GitHub does it), and three more bytes pick
a colour.  Same string in, same sigil out, forever, on any machine.
"""

from __future__ import annotations

import colorsys
import hashlib

__all__ = ["MAX_SIZE", "MIN_SIZE", "create", "digest", "grid", "palette", "render"]

MIN_SIZE = 3
MAX_SIZE = 9


def digest(name: str) -> bytes:
    """SHA-256 of the name, as raw bytes."""
    return hashlib.sha256(name.encode("utf-8")).digest()


def _bits(data: bytes):
    for byte in data:
        for shift in range(7, -1, -1):
            yield (byte >> shift) & 1


def _validate(size: int) -> None:
    if size < MIN_SIZE or size > MAX_SIZE:
        raise ValueError("size must be between %d and %d" % (MIN_SIZE, MAX_SIZE))
    if size % 2 == 0:
        raise ValueError("size must be odd, so the avatar has a centre column")


def grid(name: str, size: int = 5) -> list[list[bool]]:
    """The avatar: *size* rows of *size* booleans, mirrored left to right."""
    _validate(size)
    bits = _bits(digest(name))
    half = (size + 1) // 2
    rows = []
    for _ in range(size):
        cells = [bool(next(bits)) for _ in range(half)]
        rows.append(cells + cells[-2::-1])
    return rows


def palette(name: str) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    """Foreground and matching background colours, as 24-bit RGB triples."""
    data = digest(name)
    hue = data[0] / 255.0
    saturation = 0.45 + 0.45 * (data[1] / 255.0)
    value = 0.80 + 0.20 * (data[2] / 255.0)
    red, green, blue = colorsys.hsv_to_rgb(hue, saturation, value)
    foreground = (int(red * 255), int(green * 255), int(blue * 255))
    background = tuple(int(channel * 0.14) + 6 for channel in foreground)
    return foreground, background


def render(
    name: str,
    size: int = 5,
    *,
    colour: bool = True,
    on: str = "\u2588\u2588",
    off: str = "  ",
) -> list[str]:
    """The avatar as text.  Blocks are doubled up so the square stays square."""
    rows = grid(name, size)
    foreground, _ = palette(name)
    lines = []
    for row in rows:
        line = "".join(on if cell else off for cell in row)
        if colour:
            lines.append(
                "\x1b[38;2;%d;%d;%dm%s\x1b[0m" % (foreground[0], foreground[1], foreground[2], line)
            )
        else:
            lines.append(line)
    return lines


def create(name: str, size: int = 5) -> dict:
    """Everything about one sigil, ready for JSON."""
    foreground, background = palette(name)
    return {
        "name": name,
        "size": size,
        "sha256": digest(name).hex(),
        "grid": [
            "".join("#" if cell else "." for cell in row) for row in grid(name, size)
        ],
        "foreground": "#%02x%02x%02x" % foreground,
        "background": "#%02x%02x%02x" % background,
    }
