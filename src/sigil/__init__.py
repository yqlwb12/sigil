"""sigil -- a deterministic avatar for any string.

    >>> from sigil import render
    >>> render("alice", 5, colour=False, on="#", off=".")
    ['..#..', '.#.#.', '#####', '#.#.#', '#...#']

Same name, same sigil, on any machine: the grid comes straight out of
SHA-256 and is mirrored down the middle.
"""

from .core import MAX_SIZE, MIN_SIZE, create, digest, grid, palette, render

__version__ = "0.1.1"

__all__ = [
    "MAX_SIZE",
    "MIN_SIZE",
    "__version__",
    "create",
    "digest",
    "grid",
    "palette",
    "render",
]
