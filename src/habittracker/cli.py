"""Argument parsing and command dispatch for the `habits` CLI."""

import argparse
import sys
from datetime import date, timedelta

from . import db, render


def cmd_done(args, conn):
    habit = db.resolve_habit(conn, args.habit)
    if habit is None:
        print(f"No habit matching '{args.habit}'. Run 'habits status' to see valid habits.")
        return 1

    db.mark_done(conn, habit["id"])
    streak = db.current_streak(conn, habit["id"])
    print(f"Marked '{habit['name']}' done for today. Current streak: {streak}")
    return 0


def cmd_status(args, conn):
    habits = db.get_habits(conn)
    today = date.today()
    today_str = today.isoformat()

    today_status = {}
    entries_by_habit = {}
    week_start = today - timedelta(days=6)

    for h in habits:
        entries = db.get_entries(conn, h["id"], week_start.isoformat(), today_str)
        entries_by_habit[h["slug"]] = entries
        today_status[h["slug"]] = {
            "done": entries.get(today_str) == 1,
            "streak": db.current_streak(conn, h["id"]),
        }

    render.render_today_tiles(habits, today_status)
    print()
    render.render_week_grid(habits, entries_by_habit, today)
    return 0


def cmd_history(args, conn):
    habit = db.resolve_habit(conn, args.habit)
    if habit is None:
        print(f"No habit matching '{args.habit}'. Run 'habits status' to see valid habits.")
        return 1

    end_date = date.today()
    start_date = end_date - timedelta(days=args.days - 1)
    entries = db.get_entries(conn, habit["id"], start_date.isoformat(), end_date.isoformat())
    streak = db.current_streak(conn, habit["id"])

    render.render_history(habit, entries, start_date, end_date, streak)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="habits", description="A command-line habit tracker.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    done_parser = subparsers.add_parser("done", help="Mark a habit complete for today")
    done_parser.add_argument("habit", help="Habit slug or name, e.g. 'water' or 'workout'")
    done_parser.set_defaults(func=cmd_done)

    status_parser = subparsers.add_parser("status", help="Show today's habit tiles and streaks")
    status_parser.set_defaults(func=cmd_status)

    history_parser = subparsers.add_parser("history", help="Show a habit's recent history")
    history_parser.add_argument("habit", help="Habit slug or name, e.g. 'water' or 'workout'")
    history_parser.add_argument(
        "--days", type=int, default=30, help="Number of days to show (default: 30)"
    )
    history_parser.set_defaults(func=cmd_history)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    conn = db.connect()
    try:
        return args.func(args, conn)
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
