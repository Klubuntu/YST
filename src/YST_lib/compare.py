from YST_lib.cli import format_duration
from colorama import Style

from YST_lib.dashboard import format_number

COLUMNS = (
    ("video_id", "Video", 12),
    ("video_views", "Views", 12),
    ("video_likes", "Likes", 10),
    ("video_comments", "Comments", 9),
    ("like_ratio", "Like%", 7),
    ("comment_ratio", "Comment%", 9),
    ("views_per_hour", "Views/h", 11),
)


def ratio(part, whole):
    if not whole:
        return None
    return part / whole * 100


def views_per_hour(views, duration):
    if not duration:
        return None
    return views / (duration / 3600)


def format_compact(value):
    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}k"
    return format_number(value)


def build_rows(videos):
    rows = []
    for video in videos:
        views = video.get("video_views", 0)
        likes = video.get("video_likes", 0)
        comments = video.get("video_comments", 0)
        rows.append(
            {
                "video_id": video.get("video_id", ""),
                "video_title": video.get("video_title"),
                "video_views": views,
                "video_likes": likes,
                "video_comments": comments,
                "like_ratio": ratio(likes, views),
                "comment_ratio": ratio(comments, views),
                "views_per_hour": views_per_hour(views, video.get("video_duration")),
                "video_duration": video.get("video_duration"),
            }
        )
    return rows


def _cell(key, row, width):
    value = row.get(key)
    if key == "video_id":
        return str(value or "")[:width].ljust(width)
    if value is None:
        return "n/a".rjust(width)
    if key in ("like_ratio", "comment_ratio"):
        return f"{value:.2f}%".rjust(width)
    if key == "views_per_hour":
        return f"{format_compact(value)}/h".rjust(width)
    return format_number(value).rjust(width)


def format_table(rows):
    header = " ".join(label.rjust(width) for _, label, width in COLUMNS)
    lines = [header, "-" * len(header)]
    for row in rows:
        lines.append(" ".join(_cell(key, row, width) for key, _, width in COLUMNS))
    return lines


def format_legend(rows):
    legend = [
        f"{row['video_id']} = {row['video_title']} ({format_duration(row['video_duration'])})"
        for row in rows
        if row.get("video_title")
    ]
    return legend


def print_table(rows):
    for line in format_table(rows):
        print(line)
    for line in format_legend(rows):
        print(f"{Style.DIM}{line}{Style.RESET_ALL}")
    print("")