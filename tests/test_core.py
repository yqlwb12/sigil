"""Tests for the avatar generator."""

import json
import unittest

from sigil.core import MAX_SIZE, MIN_SIZE, create, digest, grid, palette, render


class GridTest(unittest.TestCase):
    def test_same_name_same_grid(self):
        self.assertEqual(grid("alice"), grid("alice"))

    def test_different_names_differ(self):
        self.assertNotEqual(grid("alice"), grid("bob"))

    def test_shape(self):
        for size in (3, 5, 7, 9):
            rows = grid("someone", size)
            self.assertEqual(len(rows), size)
            self.assertTrue(all(len(row) == size for row in rows))

    def test_rows_are_mirrored(self):
        for row in grid("mirror please"):
            self.assertEqual(row, row[::-1])

    def test_grid_is_boolean(self):
        for row in grid("booleans"):
            self.assertTrue(all(isinstance(cell, bool) for cell in row))

    def test_cells_actually_vary(self):
        flat = [cell for row in grid("variety is the spice of life") for cell in row]
        self.assertIn(True, flat)
        self.assertIn(False, flat)

    def test_size_validation(self):
        for bad in (1, 2, 4, MAX_SIZE + 2):
            with self.assertRaises(ValueError):
                grid("x", bad)

    def test_empty_name_is_allowed(self):
        self.assertEqual(len(grid("", 5)), 5)


class PaletteTest(unittest.TestCase):
    def test_channels_are_bytes(self):
        foreground, background = palette("alice")
        for triple in (foreground, background):
            self.assertEqual(len(triple), 3)
            self.assertTrue(all(0 <= channel <= 255 for channel in triple))

    def test_background_is_darker(self):
        foreground, background = palette("alice")
        self.assertLess(sum(background), sum(foreground))

    def test_palette_is_stable(self):
        self.assertEqual(palette("alice"), palette("alice"))


class RenderTest(unittest.TestCase):
    def test_plain_render_is_ascii(self):
        for line in render("alice", 5, colour=False, on="#", off="."):
            line.encode("ascii")
            self.assertEqual(len(line), 5)

    def test_colour_render_uses_ansi(self):
        lines = render("alice", 5, colour=True)
        self.assertTrue(all("\x1b[38;2;" in line for line in lines))

    def test_same_shape_in_both_modes(self):
        plain = render("alice", 5, colour=False, on="#", off=".")
        fancy = render("alice", 5, colour=True)
        self.assertEqual(len(plain), len(fancy))


class CreateTest(unittest.TestCase):
    def test_payload(self):
        payload = create("alice", 5)
        self.assertEqual(sorted(payload), sorted(
            ["background", "foreground", "grid", "name", "sha256", "size"]
        ))
        self.assertEqual(payload["name"], "alice")
        self.assertEqual(len(payload["sha256"]), 64)
        self.assertEqual(len(payload["grid"]), 5)
        self.assertTrue(payload["foreground"].startswith("#"))
        json.dumps(payload)  # must be serialisable

    def test_sha256_matches_hashlib(self):
        import hashlib

        self.assertEqual(digest("alice").hex(), hashlib.sha256(b"alice").hexdigest())


if __name__ == "__main__":
    unittest.main()
