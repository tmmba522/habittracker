import os
import sys
import unittest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, SRC)

from habittracker import colors  # noqa: E402


class ColorsTestCase(unittest.TestCase):
    def test_hex_to_rgb(self):
        self.assertEqual(colors.hex_to_rgb("#4A90E2"), (0x4A, 0x90, 0xE2))

    def test_fg_wraps_text_with_ansi_codes(self):
        result = colors.fg("hi", "#4A90E2")
        self.assertTrue(result.startswith("\x1b[38;2;74;144;226m"))
        self.assertTrue(result.endswith(colors.RESET))
        self.assertIn("hi", result)

    def test_bg_picks_readable_foreground(self):
        light_bg = colors.bg("x", "#F5A623")
        self.assertIn("38;2;0;0;0", light_bg)  # black text on a light background

    def test_faded_uses_dim_code(self):
        result = colors.faded("x")
        self.assertTrue(result.startswith(colors.DIM))


if __name__ == "__main__":
    unittest.main()
