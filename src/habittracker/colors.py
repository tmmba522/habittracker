"""ANSI truecolor helpers for rendering colored terminal output."""

RESET = "\x1b[0m"
DIM = "\x1b[2m"


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _luminance(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b


def readable_fg(hex_color):
    """Pick black or white foreground text for contrast against a background color."""
    r, g, b = hex_to_rgb(hex_color)
    return "#000000" if _luminance(r, g, b) > 150 else "#ffffff"


def fg(text, hex_color):
    r, g, b = hex_to_rgb(hex_color)
    return f"\x1b[38;2;{r};{g};{b}m{text}{RESET}"


def bg(text, hex_color, fg_hex=None):
    r, g, b = hex_to_rgb(hex_color)
    fg_hex = fg_hex or readable_fg(hex_color)
    fr, fg_, fb = hex_to_rgb(fg_hex)
    return f"\x1b[48;2;{r};{g};{b}m\x1b[38;2;{fr};{fg_};{fb}m{text}{RESET}"


def faded(text):
    return f"{DIM}{text}{RESET}"
