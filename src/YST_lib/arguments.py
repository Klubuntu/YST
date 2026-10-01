import copy
import sys

from colorama import Fore, Style

from YST_lib.required import *
from YST_lib.cli import (
    STAT_FILES,
    check_arg,
    extract_channel_id,
    extract_video_id,
    parse_bool,
    parse_int,
    resolve_log_selection,
)


def prompt(label, message):
    try:
        value = input(f"{Style.BRIGHT}{message}").strip()
    except EOFError:
        sys.exit(f"{Fore.LIGHTRED_EX}No Found {label} ID or Youtube Link{Style.RESET_ALL}")
    except KeyboardInterrupt:
        sys.exit(f"{Fore.LIGHTRED_EX}Cancelled{Style.RESET_ALL}")
    if len(value) < 2:
        sys.exit(f"{Fore.LIGHTRED_EX}No Found {label} ID or Youtube Link{Style.RESET_ALL}")
    return value


arguments = check_arg()
arguments2 = copy.copy(arguments)

log_mode = parse_bool(arguments.get("log_mode"), logmode)
latest_video = parse_bool(arguments.get("latest_video"), get_latest_video)
sleep_time = parse_int(arguments.get("sleep_time"), sleep_time, "sleep_time")
list_logs = parse_bool(arguments.get("list_logs"), False)
log_selection = resolve_log_selection(arguments.get("enable_log"), arguments.get("disable_log"))

if list_logs:
    print(f"{Style.BRIGHT}Available metrics:{Style.RESET_ALL}")
    for key, filename in STAT_FILES.items():
        print(f"  {Fore.YELLOW}{key:<16}{Style.RESET_ALL} -> {filename}")
    sys.exit(0)

if not arguments2.get("channel_id"):
    arguments2["channel_id"] = prompt("Channel", "Paste Your Channel ID or Youtube Link > ")
if not latest_video and not arguments2.get("video_id"):
    arguments2["video_id"] = prompt("Video", "Paste Your Video ID or Youtube Link > ")

arguments2["channel_id"] = extract_channel_id(arguments2["channel_id"])
if arguments2.get("video_id"):
    arguments2["video_id"] = extract_video_id(arguments2["video_id"])

options = {
    "channel_id": arguments2["channel_id"],
    "video_id": arguments2.get("video_id"),
    "sleep_time": sleep_time,
    "log_mode": log_mode,
    "latest_video": latest_video,
    "log_selection": log_selection,
}
