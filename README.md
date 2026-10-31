# sigil

[![tests](https://github.com/yqlwb12/sigil/actions/workflows/ci.yml/badge.svg)](https://github.com/yqlwb12/sigil/actions/workflows/ci.yml)

**A deterministic avatar for any string.** SHA-256 in, mirrored grid out: the same name gives the same sigil, forever, on any machine and in any terminal.

```console
$ sigil --ascii --no-colour alice bob carol dave
..#..   #...#   .#.#.   .###.
.#.#.   .....   .###.   .....
#####   .###.   .....   .###.
#.#.#   .###.   .#.#.   ##.##
#...#   .###.   .###.   #.#.#
alice    bob    carol    dave
```

With a 24-bit terminal the blocks come out in the name's own colour, picked from the
same hash:

```console
$ sigil alice
```

## Why

Every service wants an identicon: something stable and recognisable that identifies an
account without storing an image. They are also a nice little exercise in doing a lot
with almost nothing — no palette files, no PRNG state, no database, just a hash and a
mirror.

## Install

```console
$ pip install .
$ sigil alice
```

Or from the checkout: `PYTHONPATH=src python -m sigil alice`.

## Usage

```console
$ sigil alice                   # one avatar, 5x5
$ sigil alice bob carol         # side by side
$ sigil -s 7 alice              # bigger grid (odd sizes, 3 to 9)
$ sigil --ascii alice           # # and . instead of blocks
$ sigil --no-colour alice       # no ANSI at all
$ sigil --json alice            # hash, grid and colours as JSON
$ sigil --json alice | jq '.[0].foreground'
```

| Option | Meaning |
| --- | --- |
| `-s, --size` | grid size, odd, 3–9 (default 5) |
| `--ascii` | `#`/`.` instead of full blocks |
| `--no-colour` / `--color` | force colour off or on |
| `--no-label` | omit the names under the avatars |
| `--json` | machine-readable output |

## How it works

1. `sha256(name)` — UTF-8, no salt, no truncation.
2. Read the digest as a bit stream, most significant bit first.
3. For each of `size` rows, take `(size + 1) / 2` bits for the left half.
4. Mirror the row, excluding the centre column, so every avatar has a spine.
5. The first three bytes of the same digest become hue, saturation and value.

Five rows of five bits is 15 cells, and the leftovers give the colour — all from one
hash, so nothing has to be stored anywhere.

## Tests

```console
$ PYTHONPATH=src python -m unittest discover -s tests -v
```

27 tests: determinism, left-right symmetry (the invariant that makes a sigil look like
a sigil), grid and colour validation, ASCII-only plain output, and the JSON payload
against `hashlib` directly.

## Licence

MIT.
