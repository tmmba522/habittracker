"""Terminal rendering for the status dashboard and history views."""

from datetime import timedelta

from . import colors

TILE_WIDTH = 22
GRID_DAYS = 7
GRID_COL_WIDTH = 4


def _tile_lines(habit, done_today, streak):
    w = TILE_WIDTH - 2
    top = "╭" + "─" * w + "╮"
    bottom = "╰" + "─" * w + "╯"
    name_line = "│" + habit["name"].upper()[:w].center(w) + "│"
    blank_line = "│" + " " * w + "│"
    mark = "✓" if done_today else "·"
    mark_line = "│" + mark.center(w) + "│"
    streak_line = "│" + f"streak {streak}".center(w) + "│"

    lines = [top, name_line, blank_line, mark_line, streak_line, bottom]
    return [colors.bg(line, habit["color_hex"]) for line in lines]


def render_today_tiles(habits, today_status):
    """habits: list of habit dicts. today_status: {slug: {'done': bool, 'streak': int}}"""
    tiles = [
        _tile_lines(h, today_status[h["slug"]]["done"], today_status[h["slug"]]["streak"])
        for h in habits
    ]
    for row in zip(*tiles):
        print("  ".join(row))


def _grid_cell_padding():
    left_pad = (GRID_COL_WIDTH - 1) // 2
    right_pad = GRID_COL_WIDTH - 1 - left_pad
    return " " * left_pad, " " * right_pad


def render_week_grid(habits, entries_by_habit, end_date):
    days = [end_date - timedelta(days=i) for i in range(GRID_DAYS - 1, -1, -1)]
    label_width = max(len(h["name"]) for h in habits)

    header = " " * (label_width + 1)
    for d in days:
        header += d.strftime("%a").ljust(GRID_COL_WIDTH)
    print(header)

    left_pad, right_pad = _grid_cell_padding()
    for h in habits:
        entries = entries_by_habit.get(h["slug"], {})
        line = h["name"].ljust(label_width) + " "
        for d in days:
            done = entries.get(d.isoformat()) == 1
            colored_symbol = (
                colors.fg("■", h["color_hex"]) if done else colors.faded("■")
            )
            line += left_pad + colored_symbol + right_pad
        print(line)


def render_history(habit, entries, start_date, end_date, streak):
    total_days = (end_date - start_date).days + 1
    completed = sum(1 for v in entries.values() if v == 1)
    pct = round((completed / total_days) * 100) if total_days else 0

    title = colors.fg(habit["name"].upper(), habit["color_hex"])
    print(f"{title}  (last {total_days} days)")
    print(f"{completed}/{total_days} days completed ({pct}%) - current streak: {streak}")
    print()

    day = start_date
    row = []
    row_start = day
    while day <= end_date:
        done = entries.get(day.isoformat()) == 1
        symbol = colors.fg("■", habit["color_hex"]) if done else colors.faded("■")
        row.append(symbol)
        if len(row) == 7 or day == end_date:
            label = f"{row_start.isoformat()} to {day.isoformat()}"
            print(f"{label}: {' '.join(row)}")
            row = []
            row_start = day + timedelta(days=1)
        day += timedelta(days=1)
