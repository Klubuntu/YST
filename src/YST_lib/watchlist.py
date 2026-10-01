from colorama import Fore, Style

from YST_lib.dashboard import format_number

CHANNEL_COLUMNS = (
    ("channel_id", "Channel", 24),
    ("subs", "Subs", 12),
    ("channel_views", "Views", 14),
    ("channel_videos", "Videos", 8),
    ("views_per_video", "Views/video", 13),
)


def views_per_video(views, videos):
    if not videos:
        return None
    return views / videos


def build_rows(channels):
    rows = []
    for channel in channels:
        views = channel.get("channel_views", 0)
        videos = channel.get("channel_videos", 0)
        rows.append(
            {
                "channel_id": channel.get("channel_id", ""),
                "channel_title": channel.get("channel_title"),
                "subs": channel.get("subs", 0),
                "channel_views": views,
                "channel_videos": videos,
                "views_per_video": views_per_video(views, videos),
            }
        )
    return rows


def _cell(key, row, width):
    value = row.get(key)
    if key == "channel_id":
        return str(value or "")[:width].ljust(width)
    if value is None:
        return "n/a".rjust(width)
    if key == "views_per_video":
        return format_number(value).rjust(width)
    return format_number(value).rjust(width)


def format_table(rows):
    header = " ".join(label.rjust(width) for _, label, width in CHANNEL_COLUMNS)
    lines = [header, "-" * len(header)]
    for row in rows:
        lines.append(" ".join(_cell(key, row, width) for key, _, width in CHANNEL_COLUMNS))
    return lines


def format_legend(rows):
    return [
        f"{row['channel_id']} = {row['channel_title']}"
        for row in rows
        if row.get("channel_title")
    ]


def print_table(rows):
    for line in format_table(rows):
        print(line)
    for line in format_legend(rows):
        print(f"{Style.DIM}{line}{Style.RESET_ALL}")
    print("")


def parse_watchlist(path):
    if not path:
        return []
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError as e:
        raise SystemExit(f"{Fore.LIGHTRED_EX}Cannot read watchlist '{path}': {e}{Style.RESET_ALL}")
    entries = []
    for line in lines:
        entry = line.split("#", 1)[0].strip()
        if entry and entry not in entries:
            entries.append(entry)
    return entries


def render_watchlist(rows):
    lines = []
    for row in rows:
        hidden = row.get("subs_hidden")
        subs = "hidden" if hidden else format_number(row.get("subs", 0))
        lines.append(
            f"{row['channel_id']:<24} subs {subs:>12}   views {format_number(row.get('channel_views', 0)):>16}"
            f"   videos {format_number(row.get('channel_videos', 0)):>8}"
        )
    return lines


def print_watchlist(rows):
    for line in render_watchlist(rows):
        print(line)
    print("")

