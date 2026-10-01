import os
import sys
from time import localtime, sleep, strftime, time

import requests
from colorama import Fore, Style

from YST_lib.arguments import STAT_FILES, options
from YST_lib.cli import api_error_message, extract_channel_id, parse_duration, parse_published_at
from YST_lib.banner import print_banner
from YST_lib.compare import build_rows, print_table
from YST_lib.dashboard import ROW_ORDER, print_deltas, print_details, print_summary
from YST_lib.exporter import save
from YST_lib.report import CHART_KEYS, render_report, save_report
from YST_lib.watchlist import (
    build_rows as build_channel_rows,
    parse_watchlist,
    print_table as print_channel_table,
    print_watchlist,
)
from YST_lib.history import changes, connect, delta, latest, record, series, window
from YST_lib.required import (
    API_KEY,
    API_URL,
    REQUEST_TIMEOUT,
    ensure_output_dir,
    sep,
    soft_dir,
)


def date():
    current_time = strftime("(%d-%m-%Y) - %H:%M:%S", localtime())
    print(f"{Style.NORMAL}{current_time}{Style.RESET_ALL}")


def write_stats(values):
    ensure_output_dir()
    for key, value in values.items():
        if key not in options["log_selection"]:
            continue
        filename = STAT_FILES[key]
        try:
            with open(os.path.join(soft_dir, filename), "w") as f:
                f.write(str(value))
        except OSError as e:
            print(f"{Fore.LIGHTRED_EX}Cannot write '{filename}': {e}{Style.RESET_ALL}")
            sys.exit(1)


def fetch_statistics(url):
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as e:
        print(f"{Fore.LIGHTRED_EX}Network error: {e}{Style.RESET_ALL}")
        sys.exit(1)

    try:
        payload = response.json()
    except ValueError:
        payload = {}

    if not response.ok:
        print(f"{Fore.LIGHTRED_EX}{api_error_message(response, payload)}{Style.RESET_ALL}")
        sys.exit(1)
    return payload


def get_latest_video_id(channel_id):
    query = f"{API_URL}/search?part=snippet&channelId={channel_id}&maxResults=1&type=video&order=date&key={API_KEY}"
    data = fetch_statistics(query)
    try:
        return data["items"][0]["id"]["videoId"]
    except (KeyError, IndexError, TypeError):
        print(f"{Fore.LIGHTRED_EX}No videos found for this channel{Style.RESET_ALL}")
        sys.exit(1)


def request_channel(channel_id):
    query = f"{API_URL}/channels?part=statistics&id={channel_id}&key={API_KEY}"
    try:
        statistics = fetch_statistics(query)["items"][0]["statistics"]
    except (KeyError, IndexError, TypeError):
        print(f"{Fore.LIGHTRED_EX}Invalid URL or Channel ID{Style.RESET_ALL}")
        sys.exit(1)

    hidden = bool(statistics.get("hiddenSubscriberCount", False))
    values = {
        "subs": statistics.get("subscriberCount", 0),
        "channel_videos": statistics.get("videoCount", 0),
        "channel_views": statistics.get("viewCount", 0),
    }
    if hidden:
        values["subs"] = 0
    write_stats(values)
    return values, {"subs_hidden": hidden, "subs_visible": not hidden}


def request_video(video_id):
    query = f"{API_URL}/videos?part=snippet,contentDetails,statistics&id={video_id}&key={API_KEY}"
    try:
        item = fetch_statistics(query)["items"][0]
    except (KeyError, IndexError, TypeError):
        print(f"{Fore.LIGHTRED_EX}Invalid URL or Video ID{Style.RESET_ALL}")
        sys.exit(1)

    statistics = item.get("statistics", {})
    values = {
        "video_views": statistics.get("viewCount", 0),
        "video_likes": statistics.get("likeCount", 0),
        "video_comments": statistics.get("commentCount", 0),
    }
    write_stats(values)
    snippet = item.get("snippet", {})
    details = item.get("contentDetails", {})
    return values, {
        "video_title": snippet.get("title"),
        "video_duration": parse_duration(details.get("duration")),
        "video_published_at": parse_published_at(snippet.get("publishedAt")),
    }


def show(database, channel_id, video_id, values, meta, previous):
    print_deltas(
        values,
        delta(previous, values),
        options["log_selection"],
        hidden=meta.get("subs_hidden", False),
    )
    print_details(meta)
    if not options["dashboard"]:
        return
    hours = options["history_hours"]
    summary = changes(database, channel_id, video_id, hours)
    samples = {key: series(database, channel_id, key, video_id, hours) for key in ROW_ORDER}
    print_summary(summary, hours, samples, options["chart"])


def collect(channel_id, video_id):
    channel, channel_meta = request_channel(channel_id)
    video, meta = request_video(video_id)
    return {**channel, **video}, {**channel_meta, **meta}


def take_snapshot(database, channel_id, video_id, values, meta, last_snapshot):
    previous = latest(database, channel_id, video_id)
    now = int(time())
    if last_snapshot is None or now - last_snapshot >= options["snapshot_time"]:
        record(database, channel_id, video_id, values, {**meta, "subs_hidden": int(meta.get("subs_hidden", False))})
        return now, previous
    return last_snapshot, previous


def fetch_videos(video_ids):
    joined = ",".join(video_ids)
    query = f"{API_URL}/videos?part=snippet,contentDetails,statistics&id={joined}&key={API_KEY}"
    try:
        items = fetch_statistics(query)["items"]
    except (KeyError, IndexError, TypeError):
        print(f"{Fore.LIGHTRED_EX}No videos found for the given IDs{Style.RESET_ALL}")
        sys.exit(1)

    videos = []
    for item in items:
        statistics = item.get("statistics", {})
        details = item.get("contentDetails", {})
        snippet = item.get("snippet", {})
        videos.append(
            {
                "video_id": item.get("id", ""),
                "video_title": snippet.get("title"),
                "video_duration": parse_duration(details.get("duration")),
                "video_views": int(statistics.get("viewCount", 0) or 0),
                "video_likes": int(statistics.get("likeCount", 0) or 0),
                "video_comments": int(statistics.get("commentCount", 0) or 0),
            }
        )
    return videos


def fetch_channels(channel_ids):
    joined = ",".join(channel_ids)
    query = f"{API_URL}/channels?part=snippet,statistics&id={joined}&key={API_KEY}"
    try:
        items = fetch_statistics(query)["items"]
    except (KeyError, IndexError, TypeError):
        print(f"{Fore.LIGHTRED_EX}No channels found for the given IDs{Style.RESET_ALL}")
        sys.exit(1)

    channels = []
    for item in items:
        statistics = item.get("statistics", {})
        hidden = bool(statistics.get("hiddenSubscriberCount", False))
        channels.append(
            {
                "channel_id": item.get("id", ""),
                "channel_title": item.get("snippet", {}).get("title"),
                "subs_hidden": hidden,
                "subs": 0 if hidden else int(statistics.get("subscriberCount", 0) or 0),
                "channel_views": int(statistics.get("viewCount", 0) or 0),
                "channel_videos": int(statistics.get("videoCount", 0) or 0),
            }
        )
    return channels


def compare_channel_list(channel_ids):
    channels = fetch_channels(channel_ids)
    print_channel_table(build_channel_rows(channels))
    found = {channel["channel_id"] for channel in channels}
    missing = [channel_id for channel_id in channel_ids if channel_id not in found]
    if missing:
        print(f"{Style.DIM}Not found: {', '.join(missing)}{Style.RESET_ALL}\n")


def watch_channels(database, channel_ids, last_snapshots):
    channels = fetch_channels(channel_ids)
    now = int(time())
    for channel in channels:
        values = {
            "subs": channel["subs"],
            "channel_videos": channel["channel_videos"],
            "channel_views": channel["channel_views"],
        }
        channel_id = channel["channel_id"]
        previous = last_snapshots.get(channel_id)
        if previous is None or now - previous >= options["snapshot_time"]:
            record(
                database,
                channel_id,
                "",
                values,
                {"subs_hidden": channel["subs_hidden"]},
            )
            last_snapshots[channel_id] = now
    print_watchlist(channels)


def compare_videos(video_ids):
    videos = fetch_videos(video_ids)
    print_table(build_rows(videos))
    found = {video["video_id"] for video in videos}
    missing = [video_id for video_id in video_ids if video_id not in found]
    if missing:
        print(
            f"{Style.DIM}Not found: {', '.join(missing)}{Style.RESET_ALL}\n"
        )


def export_history(database, channel_id, video_id):
    export_format = options["export_format"]
    stamp = strftime("%Y%m%d-%H%M%S", localtime())
    target = save(
        database,
        export_format,
        channel_id,
        video_id,
        options["history_hours"],
        options["export_path"],
        stamp,
    )
    print(f"{Style.BRIGHT}Exported {export_format.upper()} to {Fore.YELLOW}{target}{Style.RESET_ALL}")
    return target


def write_report(database, channel_id, video_id):
    hours = options["history_hours"]
    rows = window(database, channel_id, video_id or None, hours)
    samples = {
        key: series(database, channel_id, key, video_id or None, hours) for key in CHART_KEYS
    }
    stamp = strftime("%Y%m%d-%H%M%S", localtime())
    content = render_report(rows, samples, channel_id, video_id, hours)
    target = save_report(content, options["export_path"], f"{channel_id}_{stamp}.html")
    print(f"{Style.BRIGHT}Report written to {Fore.YELLOW}{target}{Style.RESET_ALL}")
    return target


def main():
    print_banner()
    print("")
    print(f"{Style.BRIGHT}YouTube Stats Tool (v 1.0 by https://github.com/klubuntu){Style.RESET_ALL}")
    print(sep)

    channel_id = options["channel_id"]
    video_id = options["video_id"]
    ensure_output_dir()

    selection = options["log_selection"]
    if selection != set(STAT_FILES):
        print(f"{Style.BRIGHT}Logged metrics: {Fore.YELLOW}{', '.join(sorted(selection))}{Style.RESET_ALL}")

    if options["compare"]:
        compare_videos(options["compare"])
        return

    if options["compare_channels"]:
        compare_channel_list(options["compare_channels"])
        return

    database = connect(options["history_path"])

    if options["watchlist"]:
        watch_ids = []
        for entry in parse_watchlist(options["watchlist"]):
            resolved = extract_channel_id(entry)
            if resolved not in watch_ids:
                watch_ids.append(resolved)
        if not watch_ids:
            print(f"{Fore.LIGHTRED_EX}Watchlist '{options['watchlist']}' is empty{Style.RESET_ALL}")
            sys.exit(1)
        last_snapshots = {}
        try:
            while True:
                watch_channels(database, watch_ids, last_snapshots)
                sleep(options["sleep_time"])
        except KeyboardInterrupt:
            print(f"{Fore.LIGHTRED_EX}                          User Exit                {Style.RESET_ALL}")
            sys.exit(0)

    if options["report"]:
        write_report(database, channel_id, video_id)
        return

    if options["export_format"]:
        export_history(database, channel_id, video_id)
        return

    try:
        if options["latest_video"]:
            video_id = get_latest_video_id(channel_id)
        if not video_id:
            print(f"{Fore.LIGHTRED_EX}No Video ID or Youtube Link{Style.RESET_ALL}")
            sys.exit(1)

        last_snapshot = None
        verbose = options["log_mode"] or options["dashboard"]
        if verbose:
            while True:
                date()
                values, meta = collect(channel_id, video_id)
                last_snapshot, previous = take_snapshot(
                    database, channel_id, video_id, values, meta, last_snapshot
                )
                show(database, channel_id, video_id, values, meta, previous)
                sleep(options["sleep_time"])
        else:
            progress = "-"
            print(f"Start Logging to Folder {soft_dir}")
            while True:
                values, meta = collect(channel_id, video_id)
                last_snapshot, previous = take_snapshot(
                    database, channel_id, video_id, values, meta, last_snapshot
                )
                print(f"{Fore.LIGHTYELLOW_EX}{progress}", end="\r")
                progress += "-"
                if progress == "-" * 60:
                    progress = "-"
                sleep(options["sleep_time"])
    except KeyboardInterrupt:
        print(f"{Fore.LIGHTRED_EX}                          User Exit                {Style.RESET_ALL}")
        sys.exit(0)