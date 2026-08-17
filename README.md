# Habit Tracker

A command-line habit tracker. Mark daily habits done, see today's status at a
glance as colored tiles with streaks, and review the last 30 days of any
habit. Data is stored locally in a SQLite database — nothing leaves your
machine.

## Default habits

| Habit               | Slug         | Color    |
| -------------------- | ------------ | -------- |
| Drink 100oz water     | `water`      | blue     |
| Workout                | `workout`    | orange   |
| 10k steps               | `steps`      | green    |
| 8hr sleep                | `sleep`      | lavender |
| Meditation                | `meditation` | pink     |

These are seeded automatically the first time you run any command.

## Install

Requires Python 3.8+. No third-party dependencies — everything uses the
Python standard library (including `sqlite3`).

Clone the repo, then either run it directly with no install:

```bash
git clone <this-repo-url>
cd habittracker
./bin/habits status
```

...or install it so `habits` is available anywhere on your `$PATH`:

```bash
pip install -e .
habits status
```

## Usage

Mark a habit done for today:

```bash
habits done water
habits done workout
```

`<habit>` can be the slug (`water`) or a unique fragment of the display name
(`meditat` matches "Meditation").

Show today's status — colored tiles with each habit's current streak, plus a
7-day-by-5-habit grid where faded squares mark missed days:

```bash
habits status
```

Show the last 30 days of history for one habit:

```bash
habits history water
habits history sleep --days 14   # override the window
```

## Data

Data lives in `data/habits.db` (SQLite), created on first run. The `data/`
folder is gitignored — your habit history is local to your machine and never
committed.

Set `HABITS_DB_PATH` to point at a different database file, e.g. for tests or
a demo database:

```bash
HABITS_DB_PATH=./demo.db habits status
```

### Seeding sample data

`scripts/seed_sample_data.py` loads `scripts/sample_data.csv` (a week of
sample entries across all five habits) into the database, useful for trying
out `status`/`history` without tracking real habits first:

```bash
python3 scripts/seed_sample_data.py
```

## Tests

Basic tests using Python's built-in `unittest` (no extra install needed):

```bash
python3 -m unittest discover -s tests -v
```

## Project structure

```
bin/habits              entry point script (`habits <command>`)
src/habittracker/
  db.py                  SQLite schema, default habits, queries
  colors.py              ANSI truecolor helpers for terminal output
  render.py               status tiles / week grid / history rendering
  cli.py                   argument parsing and command dispatch
scripts/
  sample_data.csv          example habit data
  seed_sample_data.py       loads sample_data.csv into the database
tests/                     unittest test suite
data/                       gitignored SQLite database (created on first run)
```
