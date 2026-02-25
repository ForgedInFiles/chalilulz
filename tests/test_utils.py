"""
test_utils — UI utility functions (sep, pvw, rmd, cols, Spin)
"""

import unittest
import sys
import os
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chalilulz import cols, sep, pvw, rmd, Spin


class TestUIUtils(unittest.TestCase):
    def test_cols_returns_int(self):
        n = cols()
        self.assertIsInstance(n, int)
        self.assertGreater(n, 0)

    def test_pvw_single_line(self):
        s = "Hello World"
        result = pvw(s, 20)
        self.assertEqual(result, "Hello World")

    def test_pvw_truncates_long(self):
        s = "A" * 100
        result = pvw(s, 20)
        self.assertIn("…", result)  # Ellipsis present (may include ANSI codes)
        self.assertLess(len(result), 50)  # Should be short

    def test_pvw_shows_line_count(self):
        s = "Line1\nLine2\nLine3"
        result = pvw(s, 10)
        self.assertIn("+2L", result)

    def test_rmd_formats_code(self):
        s = "```py\nprint('hi')\n```"
        result = rmd(s)
        self.assertIn("[code]", result)
        self.assertIn("[/code]", result)
        self.assertIn("print('hi')", result)

    def test_rmd_inline_code(self):
        s = "`x = 5`"
        result = rmd(s)
        self.assertIn("x = 5", result)

    def test_rmd_bold(self):
        s = "**bold**"
        result = rmd(s)
        self.assertIn("bold", result)

    def test_rmd_italic(self):
        s = "*italic*"
        result = rmd(s)
        self.assertIn("italic", result)


class TestSpin(unittest.TestCase):
    def test_spin_init(self):
        spinner = Spin()
        self.assertIsNotNone(spinner._e)
        self.assertIsNone(spinner._t)

    def test_spin_start_creates_thread(self):
        spinner = Spin()
        spinner.start("Testing")
        self.assertIsNotNone(spinner._t)
        self.assertTrue(spinner._t.is_alive())
        spinner.stop()

    def test_spin_stop_sets_event(self):
        spinner = Spin()
        spinner.start("Testing")
        self.assertFalse(spinner._e.is_set())
        spinner.stop()
        self.assertTrue(spinner._e.is_set())

    def test_spin_stop_joins_thread(self):
        spinner = Spin()
        spinner.start("Testing")
        spinner.stop()
        # After stop, thread should not be alive
        if spinner._t:
            self.assertFalse(spinner._t.is_alive())

    def test_spin_multiple_start_stop(self):
        spinner = Spin()
        spinner.start("First")
        if spinner._t:
            self.assertTrue(spinner._t.is_alive())
        spinner.stop()
        if spinner._t:
            self.assertFalse(spinner._t.is_alive())
        spinner.start("Second")
        if spinner._t:
            self.assertTrue(spinner._t.is_alive())
        spinner.stop()

    def test_spin_daemon_thread(self):
        spinner = Spin()
        spinner.start("Testing")
        if spinner._t:
            self.assertTrue(spinner._t.daemon)
        spinner.stop()


if __name__ == "__main__":
    unittest.main()
