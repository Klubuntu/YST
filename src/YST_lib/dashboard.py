from time import gmtime, strftime

from colorama import Fore, Style

from YST_lib.cli import format_duration

SPARK_CHARS = "▁▂▃▄▅▆▇█"

METRIC_LABELS = {
    "subs": "Subscribers",
    "channel_views": "Channel Views",
    "channel_videos": "Channel Videos",
    "video_views": "Video Views",
    "video_likes": "Video Likes",
    "video_comments": "Video Comments",
}

METRIC_COLORS = {
    "subs": Fore.LIGHTGREEN_EX,
    "channel_views": Fore.LIGHTCYAN_EX,
    "channel_videos": Fore.LIGHTBLUE_EX,
    "video_views": Fore.LIGHTYELLOW_EX,
    "video_likes": Fore.MAGENTA,
    "video_comments": Fore.LIGHTRED_EX,
}

CHART_KEYS = ("video_views", "channel_views", "subs")

ROW_ORDER = (
    "subs",
    "channel_views",
    "channel_videos",
    "video_likes",
    "video_comments",
    "video_views",
)


def format_number(value):
    return f"{int(value):,}".replace(",", " ")


def format_change(value):
    sign = "+" if value > 0 else ""
    return f"{sign}{int(value):,}".replace(",", " ")


def sparkline(points, width=30):
    values = [value for _, value in points]
    if not values:
        return ""
    if len(values) > width:
        values = downsample(values, width)
    low, high = min(values), max(values)
    if high == low:
        return SPARK_CHARS[0] * len(values)
    span = high - low
    bars = []
    for value in values:
        index = round((value - low) / span * (len(SPARK_CHARS) - 1))
        bars.append(SPARK_CHARS[index])
    return "".join(bars)


def downsample(values, width):
    if len(values) <= width:
        return list(values)
    step = len(values) / width
    sampled = [values[int(index * step)] for index in range(width)]
    sampled[-1] = values[-1]
    return sampled


def format_deltas(values, delta, selected=None, hidden=False):
    lines = []
    for key in ROW_ORDER:
        if key not in values:
            continue
        if selected is not None and key not in selected:
            continue
        color = METRIC_COLORS.get(key, "")
        label = METRIC_LABELS.get(key, key)
        if key == "subs" and hidden:
            lines.append(f"{color}{label}: hidden by the channel{Style.RESET_ALL}")
            continue
        line = f"{color}{label}: {format_number(values[key])}"
        if delta and key in delta:
            line += f" {Style.DIM}({format_change(delta[key])}){Style.RESET_ALL}"
        lines.append(f"{line}{Style.RESET_ALL}")
    return lines


def render_chart(points, height=10, width=60):
    if len(points) < 2:
        return []
    values = downsample([value for _, value in points], width)
    if len(values) < 2:
        return []
    low, high = min(values), max(values)
    span = high - low or 1
    levels = len(SPARK_CHARS)

    rows = [[] for _ in range(height)]
    for value in values:
        filled = (value - low) / span * (height * levels)
        for row in range(height):
            offset = filled - row * levels
            index = max(min(int(offset), levels - 1), 0)
            rows[row].append(SPARK_CHARS[index])

    lines = ["".join(row) for row in rows]
    left, right = format_number(low), format_number(high)
    gap = max(len(values) - len(left) - len(right), 1)
    lines.append(left + " " * gap + right)
    return lines


def format_chart(points, label, height=10):
    chart = render_chart(points, height)
    if not chart:
        return []
    color = METRIC_COLORS.get(label, "")
    return [f"{color}{line}{Style.RESET_ALL}" for line in chart]


def format_summary(changes, hours, samples, spark_key="video_views"):
    if not changes:
        return [
            f"{Style.BRIGHT}History:{Style.RESET_ALL} {Fore.YELLOW}no snapshots in the last {hours}h{Style.RESET_ALL}"
        ]

    lines = [f"{Style.BRIGHT}Last {hours}h:{Style.RESET_ALL}"]
    for key in ROW_ORDER:
        change = changes.get(key)
        if not change:
            continue
        lines.append(
            f"{METRIC_COLORS.get(key, '')}{METRIC_LABELS.get(key, key)}: "
            f"{format_change(change['change'])} "
            f"{Style.DIM}({format_change(change['per_hour'])}/h){Style.RESET_ALL}"
        )
    trend = sparkline(samples.get(spark_key, []))
    if trend:
        lines.append(
            f"{METRIC_COLORS.get(spark_key, '')}{METRIC_LABELS.get(spark_key, spark_key)} trend:"
            f"{Style.RESET_ALL} {trend}"
        )
    lines.append(f"{Style.DIM}Member and subscriber status are not exposed by the YouTube Data API v3{Style.RESET_ALL}")
    return lines


def format_details(meta):
    if not meta:
        return []
    lines = []
    title = meta.get("video_title")
    if title:
        lines.append(f"{Style.BRIGHT}Video:{Style.RESET_ALL} {title}")
    duration = format_duration(meta.get("video_duration"))
    published = meta.get("video_published_at")
    when = strftime("%d-%m-%Y", gmtime(published)) if published else "unknown"
    lines.append(f"{Style.DIM}Published:{Style.RESET_ALL} {when}   Length: {duration}")
    return lines


def print_deltas(values, delta, selected=None, hidden=False):
    for line in format_deltas(values, delta, selected, hidden):
        print(line)
    print("")


def print_summary(changes, hours, samples, charts=False):
    lines = format_summary(changes, hours, samples)
    if charts:
        for key in CHART_KEYS:
            block = format_chart(samples.get(key, []), key)
            if block:
                lines.append(f"{METRIC_COLORS.get(key, '')}{METRIC_LABELS.get(key, key)}:{Style.RESET_ALL}")
                lines.extend(block)
    for line in lines:
        print(line)
    print("")

def print_details(meta):
    lines = format_details(meta)
    for line in lines:
        print(line)
    if lines:
        print("")
