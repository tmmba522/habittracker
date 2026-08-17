import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, SRC)

from habittracker import cli  # noqa: E402


class CliTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test.db")
        os.environ["HABITS_DB_PATH"] = self.db_path

    def tearDown(self):
        del os.environ["HABITS_DB_PATH"]
        self.tmpdir.cleanup()

    def run_cli(self, argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(argv)
        return code, buf.getvalue()

    def test_done_marks_habit_complete(self):
        code, out = self.run_cli(["done", "water"])
        self.assertEqual(code, 0)
        self.assertIn("Drink 100oz water", out)
        self.assertIn("streak: 1", out)

    def test_done_unknown_habit_returns_error(self):
        code, out = self.run_cli(["done", "flying"])
        self.assertEqual(code, 1)
        self.assertIn("No habit matching", out)

    def test_status_lists_all_habit_names(self):
        self.run_cli(["done", "water"])
        code, out = self.run_cli(["status"])
        self.assertEqual(code, 0)
        for name in ["WATER", "WORKOUT", "STEPS", "SLEEP", "MEDITATION"]:
            self.assertIn(name, out)

    def test_history_shows_completion_summary(self):
        self.run_cli(["done", "steps"])
        code, out = self.run_cli(["history", "steps", "--days", "7"])
        self.assertEqual(code, 0)
        self.assertIn("1/7 days completed", out)


if __name__ == "__main__":
    unittest.main()
