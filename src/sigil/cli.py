"""Command line front end for sigil."""

from __future__ import annotations

import argparse
import json
import sys

from .core import MAX_SIZE, MIN_SIZE, create, render

__version__ = "0.1.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sigil",
        description="A deterministic avatar for any string: same name, same sigil.",
        epilog="examples:\n  sigil alice\n  sigil alice bob carol\n  sigil --size 7 --ascii alice",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("names", nargs="+", metavar="NAME", help="one or more names")
    parser.add_argument("-s", "--size", type=int, default=5, metavar="N",
                        help="grid size, odd, %d-%d (default 5)" % (MIN_SIZE, MAX_SIZE))
    parser.add_argument("--ascii", action="store_true",
                        help="use # and . instead of blocks")
    parser.add_argument("--no-colour", "--no-color", dest="colour",
                        action="store_false", help="no ANSI colour")
    parser.add_argument("--color", "--colour", dest="force_colour", action="store_true",
                        help="emit colour even when stdout is not a terminal")
    parser.add_argument("--no-label", action="store_true",
                        help="omit the names under the avatars")
    parser.add_argument("--json", action="store_true", help="machine readable output")
    parser.add_argument("--version", action="version", version="sigil " + __version__)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.json:
        payload = [create(name, args.size) for name in args.names]
        sys.stdout.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        return 0

    try:
        colour = args.force_colour or (args.colour and sys.stdout.isatty())
        on, off = ("#", ".") if args.ascii else ("\u2588\u2588", "  ")
        blocks = [render(name, args.size, colour=colour, on=on, off=off) for name in args.names]
    except ValueError as exc:
        parser.error(str(exc))

    width = args.size * len(on)
    for row in range(args.size):
        sys.stdout.write("   ".join(block[row] for block in blocks) + "\n")
    if not args.no_label:
        sys.stdout.write(
            "   ".join(name[:width].center(width) for name in args.names) + "\n"
        )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
