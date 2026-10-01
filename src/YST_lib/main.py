import json
import os
import sys
from time import localtime, sleep, strftime

from colorama import Fore, Style

from YST_lib.required import *
from YST_lib.arguments import *
from YST_lib.banner import print_banner


def date():
    current_time = strftime("(%d-%m-%Y) - %H:%M:%S", localtime())
    print(f"{Style.NORMAL}{current_time}{Style.RESET_ALL}")


def write_stat(filename, value):
    ensure_output_dir()
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

    write_stat("channel_subscribers.txt", statistics.get("subscriberCount", 0))
    write_stat("channel_videoCount.txt", statistics.get("videoCount", 0))
    write_stat("channel_viewsCount.txt", statistics.get("viewCount", 0))
    return statistics


def request_video(video_id):
    query = f"{API_URL}/videos?part=statistics&id={video_id}&key={API_KEY}"
    try:
        statistics = fetch_statistics(query)["items"][0]["statistics"]
    except (KeyError, IndexError, TypeError):
        print(f"{Fore.LIGHTRED_EX}Invalid URL or Video ID{Style.RESET_ALL}")
        sys.exit(1)

    write_stat("video_views.txt", statistics.get("viewCount", 0))
    write_stat("video_likes.txt", statistics.get("likeCount", 0))
    write_stat("video_comments.txt", statistics.get("commentCount", 0))
    return statistics


def result(channel, video):
    print(f"{Fore.LIGHTGREEN_EX}Subscribers: {channel.get('subscriberCount', 0)}")
    print(f"{Fore.LIGHTCYAN_EX}Channel Views: {channel.get('viewCount', 0)}")
    print(f"{Fore.LIGHTBLUE_EX}Channel Videos: {channel.get('videoCount', 0)}")
    print(f"{Fore.MAGENTA}Video Likes: {video.get('likeCount', 0)}")
    print(f"{Fore.LIGHTRED_EX}Video Comments: {video.get('commentCount', 0)}")
    print(f"{Fore.LIGHTYELLOW_EX}Video Views: {video.get('viewCount', 0)}{Style.RESET_ALL}")
    print("")


def main():
    print_banner()
    print("")
    print(f"{Style.BRIGHT}YouTube Stats Tool (v 1.0 by https://github.com/klubuntu){Style.RESET_ALL}")
    print(sep)

    channel_id = options["channel_id"]
    video_id = options["video_id"]
    ensure_output_dir()

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