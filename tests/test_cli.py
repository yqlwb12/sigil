"""Tests for the sigil command line."""

import io
import json
import unittest
from contextlib import redirect_stdout

from sigil import cli


def call(*argv):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = cli.main(list(argv))
    return code, buffer.getvalue()


class LayoutTest(unittest.TestCase):
    def test_single_avatar_fills_its_grid(self):
        code, out = call("--ascii", "--no-colour", "alice")
        self.assertEqual(code, 0)
        lines = out.splitlines()
        self.assertEqual(len(lines), 6)  # five rows plus the label
        self.assertTrue(all(len(line) == 5 for line in lines[:5]))
        self.assertEqual(lines[-1].strip(), "alice")

    def test_no_label(self):
        _, out = call("--ascii", "--no-colour", "--no-label", "alice")
        self.assertEqual(len(out.splitlines()), 5)

    def test_three_avatars_side_by_side(self):
        _, out = call("--ascii", "--no-colour", "alice", "bob", "carol")
        lines = out.splitlines()
        self.assertEqual(len(lines), 6)
        self.assertEqual(len(lines[0]), 5 * 3 + 2 * 3)
        self.assertIn("bob", lines[-1])

    def test_size_option(self):
        _, out = call("--ascii", "--no-colour", "-s", "7", "alice")
        self.assertEqual(len(out.splitlines()[0]), 7)

    def test_plain_output_is_ascii(self):
        _, out = call("--ascii", "--no-colour", "alice")
        out.encode("ascii")

    def test_forced_colour(self):
        _, out = call("--color", "alice")
        self.assertIn("\x1b[38;2;", out)


class JsonTest(unittest.TestCase):
    def test_payload(self):
        code, out = call("--json", "alice", "bob")
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual([entry["name"] for entry in payload], ["alice", "bob"])
        self.assertTrue(all(len(entry["sha256"]) == 64 for entry in payload))

    def test_json_is_deterministic(self):
        self.assertEqual(call("--json", "alice"), call("--json", "alice"))


class ArgumentTest(unittest.TestCase):
    def test_even_size_is_rejected(self):
        with self.assertRaises(SystemExit) as caught:
            call("-s", "4", "alice")
        self.assertEqual(caught.exception.code, 2)

    def test_json_path_rejects_even_size_too(self):
        with self.assertRaises(SystemExit) as caught:
            call("--json", "-s", "4", "alice")
        self.assertEqual(caught.exception.code, 2)

    def test_missing_name(self):
        with self.assertRaises(SystemExit) as caught:
            call()
        self.assertEqual(caught.exception.code, 2)

    def test_version(self):
        with self.assertRaises(SystemExit) as caught:
            call("--version")
        self.assertEqual(caught.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
