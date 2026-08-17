"""SQLite persistence layer for the habit tracker."""

import os
import sqlite3
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "habits.db"

# (slug, display name, color name, hex code, sort order)
DEFAULT_HABITS = [
    ("water", "Drink 100oz water", "blue", "#4A90E2", 0),
    ("workout", "Workout", "orange", "#F5A623", 1),
    ("steps", "10k steps", "green", "#34C759", 2),
    ("sleep", "8hr sleep", "lavender", "#B19CD9", 3),
    ("meditation", "Meditation", "pink", "#FF6FA0", 4),
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    color_name TEXT NOT NULL,
    color_hex TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY,
    habit_id INTEGER NOT NULL REFERENCES habits(id),
    date TEXT NOT NULL,
    completed INTEGER NOT NULL DEFAULT 1,
    UNIQUE(habit_id, date)
);
"""


def db_path():
    override = os.environ.get("HABITS_DB_PATH")
    return Path(override) if override else DEFAULT_DB_PATH


def connect(path=None):
    path = Path(path) if path else db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    init_db(conn)
    return conn


def init_db(conn):
    conn.executescript(SCHEMA)
    seed_defaults(conn)
    conn.commit()


def seed_defaults(conn):
    for slug, name, color_name, color_hex, sort_order in DEFAULT_HABITS:
        conn.execute(
            """
            INSERT INTO habits (slug, name, color_name, color_hex, sort_order)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO NOTHING
            """,
            (slug, name, color_name, color_hex, sort_order),
        )


def get_habits(conn):
    rows = conn.execute("SELECT * FROM habits ORDER BY sort_order").fetchall()
    return [dict(row) for row in rows]


def resolve_habit(conn, query):
    """Find a habit by slug (exact, case-insensitive) or a unique name match."""
    query = query.strip().lower()
    habits = get_habits(conn)

    for habit in habits:
        if habit["slug"] == query:
            return habit

    matches = [h for h in habits if query in h["name"].lower()]
    if len(matches) == 1:
        return matches[0]
    return None


def mark_done(conn, habit_id, on_date=None, completed=1):
    on_date = on_date or date.today().isoformat()
    conn.execute(
        """
        INSERT INTO entries (habit_id, date, completed)
        VALUES (?, ?, ?)
        ON CONFLICT(habit_id, date) DO UPDATE SET completed = excluded.completed
        """,
        (habit_id, on_date, completed),
    )
    conn.commit()


def get_entries(conn, habit_id, start_date, end_date):
    """Return {date_str: completed} for a habit between two ISO dates (inclusive)."""
    rows = conn.execute(
        """
        SELECT date, completed FROM entries
        WHERE habit_id = ? AND date BETWEEN ? AND ?
        """,
        (habit_id, start_date, end_date),
    ).fetchall()
    return {row["date"]: row["completed"] for row in rows}


def current_streak(conn, habit_id, on_date=None):
    """Count consecutive completed days ending at on_date (default: today)."""
    end = date.fromisoformat(on_date) if on_date else date.today()
    start = end - timedelta(days=365)
    entries = get_entries(conn, habit_id, start.isoformat(), end.isoformat())

    streak = 0
    day = end
    while entries.get(day.isoformat()) == 1:
        streak += 1
        day -= timedelta(days=1)
    return streak
