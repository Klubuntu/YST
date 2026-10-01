import os
import sys
from time import localtime, sleep, strftime

import requests
from colorama import Fore, Style

from YST_lib.arguments import STAT_FILES, options
from YST_lib.banner import print_banner
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
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as e:
        print(f"{Fore.LIGHTRED_EX}Request failed: {e}{Style.RESET_ALL}")
        sys.exit(1)


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

    write_stats(
        {
            "subs": statistics.get("subscriberCount", 0),
            "channel_videos": statistics.get("videoCount", 0),
            "channel_views": statistics.get("viewCount", 0),
        }
    )
    return statistics


def request_video(video_id):
    query = f"{API_URL}/videos?part=statistics&id={video_id}&key={API_KEY}"
    try:
        statistics = fetch_statistics(query)["items"][0]["statistics"]
    except (KeyError, IndexError, TypeError):
        print(f"{Fore.LIGHTRED_EX}Invalid URL or Video ID{Style.RESET_ALL}")
        sys.exit(1)

    write_stats(
        {
            "video_views": statistics.get("viewCount", 0),
            "video_likes": statistics.get("likeCount", 0),
            "video_comments": statistics.get("commentCount", 0),
        }
    )
    return statistics


def result(channel, video):
    rows = (
        ("subs", "Subscribers", Fore.LIGHTGREEN_EX, channel.get("subscriberCount", 0)),
        ("channel_views", "Channel Views", Fore.LIGHTCYAN_EX, channel.get("viewCount", 0)),
        ("channel_videos", "Channel Videos", Fore.LIGHTBLUE_EX, channel.get("videoCount", 0)),
        ("video_likes", "Video Likes", Fore.MAGENTA, video.get("likeCount", 0)),
        ("video_comments", "Video Comments", Fore.LIGHTRED_EX, video.get("commentCount", 0)),
        ("video_views", "Video Views", Fore.LIGHTYELLOW_EX, video.get("viewCount", 0)),
    )
    for key, label, color, value in rows:
        if key in options["log_selection"]:
            print(f"{color}{label}: {value}{Style.RESET_ALL}")
    print("")


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

    try:
        if options["latest_video"]:
            video_id = get_latest_video_id(channel_id)
        if not video_id:
            print(f"{Fore.LIGHTRED_EX}No Video ID or Youtube Link{Style.RESET_ALL}")
            sys.exit(1)

        if options["log_mode"]:
            while True:
                date()
                result(request_channel(channel_id), request_video(video_id))
                sleep(options["sleep_time"])
        else:
            progress = "-"
            print(f"Start Logging to Folder {soft_dir}")
            while True:
                request_channel(channel_id)
                request_video(video_id)
                print(f"{Fore.LIGHTYELLOW_EX}{progress}", end="\r")
                progress += "-"
                if progress == "-" * 60:
                    progress = "-"
                sleep(options["sleep_time"])
    except KeyboardInterrupt:
        print(f"{Fore.LIGHTRED_EX}                          User Exit                {Style.RESET_ALL}")
        sys.exit(0)