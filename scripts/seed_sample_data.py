#!/usr/bin/env python3
"""Load scripts/sample_data.csv into the habits database for demo purposes.

Usage: python3 scripts/seed_sample_data.py
"""

import csv
import os
import sys

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, SRC)

from habittracker import db  # noqa: E402

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data.csv")


def main():
    conn = db.connect()
    habits_by_slug = {h["slug"]: h for h in db.get_habits(conn)}

    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            habit = habits_by_slug.get(row["habit"])
            if habit is None:
                print(f"Skipping unknown habit '{row['habit']}'")
                continue
            db.mark_done(conn, habit["id"], on_date=row["date"], completed=int(row["completed"]))
            count += 1

    conn.close()
    print(f"Seeded {count} entries from {CSV_PATH}")


if __name__ == "__main__":
    main()
