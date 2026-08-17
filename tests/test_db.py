import os
import sys
import tempfile
import unittest
from datetime import date, timedelta

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, SRC)

from habittracker import db  # noqa: E402


class DbTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test.db")
        self.conn = db.connect(self.db_path)

    def tearDown(self):
        self.conn.close()
        self.tmpdir.cleanup()

    def test_seeds_five_default_habits(self):
        habits = db.get_habits(self.conn)
        self.assertEqual(len(habits), 5)
        slugs = {h["slug"] for h in habits}
        self.assertEqual(slugs, {"water", "workout", "steps", "sleep", "meditation"})

    def test_default_habit_colors(self):
        habits = {h["slug"]: h for h in db.get_habits(self.conn)}
        self.assertEqual(habits["water"]["color_name"], "blue")
        self.assertEqual(habits["workout"]["color_name"], "orange")
        self.assertEqual(habits["steps"]["color_name"], "green")
        self.assertEqual(habits["sleep"]["color_name"], "lavender")
        self.assertEqual(habits["meditation"]["color_name"], "pink")

    def test_resolve_habit_by_slug(self):
        habit = db.resolve_habit(self.conn, "water")
        self.assertIsNotNone(habit)
        self.assertEqual(habit["slug"], "water")

    def test_resolve_habit_is_case_insensitive(self):
        habit = db.resolve_habit(self.conn, "WORKOUT")
        self.assertIsNotNone(habit)
        self.assertEqual(habit["slug"], "workout")

    def test_resolve_habit_by_name_fragment(self):
        habit = db.resolve_habit(self.conn, "meditat")
        self.assertIsNotNone(habit)
        self.assertEqual(habit["slug"], "meditation")

    def test_resolve_unknown_habit_returns_none(self):
        self.assertIsNone(db.resolve_habit(self.conn, "flying"))

    def test_mark_done_and_read_back(self):
        habit = db.resolve_habit(self.conn, "water")
        today = date.today().isoformat()
        db.mark_done(self.conn, habit["id"], on_date=today)
        entries = db.get_entries(self.conn, habit["id"], today, today)
        self.assertEqual(entries[today], 1)

    def test_mark_done_is_idempotent_per_day(self):
        habit = db.resolve_habit(self.conn, "steps")
        today = date.today().isoformat()
        db.mark_done(self.conn, habit["id"], on_date=today)
        db.mark_done(self.conn, habit["id"], on_date=today)
        entries = db.get_entries(self.conn, habit["id"], today, today)
        self.assertEqual(len(entries), 1)

    def test_current_streak_counts_consecutive_days(self):
        habit = db.resolve_habit(self.conn, "sleep")
        today = date.today()
        for offset in range(3):
            day = (today - timedelta(days=offset)).isoformat()
            db.mark_done(self.conn, habit["id"], on_date=day)
        self.assertEqual(db.current_streak(self.conn, habit["id"]), 3)

    def test_current_streak_stops_at_gap(self):
        habit = db.resolve_habit(self.conn, "sleep")
        today = date.today()
        db.mark_done(self.conn, habit["id"], on_date=today.isoformat())
        gap_day = (today - timedelta(days=1)).isoformat()
        db.mark_done(self.conn, habit["id"], on_date=gap_day, completed=0)
        older_day = (today - timedelta(days=2)).isoformat()
        db.mark_done(self.conn, habit["id"], on_date=older_day)
        self.assertEqual(db.current_streak(self.conn, habit["id"]), 1)

    def test_current_streak_zero_when_not_done_today(self):
        habit = db.resolve_habit(self.conn, "meditation")
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        db.mark_done(self.conn, habit["id"], on_date=yesterday)
        self.assertEqual(db.current_streak(self.conn, habit["id"]), 0)


if __name__ == "__main__":
    unittest.main()
