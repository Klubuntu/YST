import copy
import re
import sys

from colorama import Fore, Style

from YST_lib.cli import (
    STAT_FILES,
    SUBCOMMAND_HELP,
    check_arg,
    extract_channel_id,
    extract_video_id,
    parse_bool,
    parse_int,
    resolve_log_selection,
)
from YST_lib.required import (
    DEFAULT_DB_PATH,
    EXPORT_FOLDER,
    EXPORT_FORMATS,
    get_latest_video,
    logmode,
    sleep_time,
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


def print_available_metrics():
    print(f"{Style.BRIGHT}Available metrics:{Style.RESET_ALL}")
    for metric_key, metric_file in STAT_FILES.items():
        print(f"  {Fore.YELLOW}{metric_key:<16}{Style.RESET_ALL} -> {metric_file}")


def parse_id_list(value):
    if not value:
        return []
    ids = [extract_video_id(name) for name in re.split(r"[,\s]+", value) if name]
    seen = []
    for video_id in ids:
        if video_id not in seen:
            seen.append(video_id)
    return seen


def parse_choice(value, choices, default):
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized not in choices:
        sys.exit(
            f"{Fore.LIGHTRED_EX}Invalid value '{value}'.{Style.RESET_ALL}\n"
            f"{Style.BRIGHT}Available: {Fore.YELLOW}{', '.join(sorted(choices))}{Style.RESET_ALL}"
        )
    return normalized


if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help", "help"):
    print(SUBCOMMAND_HELP)
    sys.exit(0)

arguments = check_arg()
arguments2 = copy.copy(arguments)

log_mode = parse_bool(arguments.get("log_mode"), logmode)
latest_video = parse_bool(arguments.get("latest_video"), get_latest_video)
sleep_time = parse_int(arguments.get("sleep_time"), sleep_time, "sleep_time")
list_logs = parse_bool(arguments.get("list_logs"), False)
log_selection = resolve_log_selection(arguments.get("enable_log"), arguments.get("disable_log"))
history_path = arguments.get("db") or DEFAULT_DB_PATH
snapshot_time = parse_int(arguments.get("snapshot_time"), 60, "snapshot_time")
history_hours = parse_int(arguments.get("history"), 24, "history")
dashboard_mode = parse_bool(arguments.get("dashboard"), False)
export_format = parse_choice(arguments.get("export"), EXPORT_FORMATS, None)
export_path = arguments.get("export_path") or EXPORT_FOLDER
compare_ids = parse_id_list(arguments.get("compare"))

if list_logs:
    print_available_metrics()
    sys.exit(0)

if not compare_ids and not arguments2.get("channel_id"):
    arguments2["channel_id"] = prompt("Channel", "Paste Your Channel ID or Youtube Link > ")
if not latest_video and not export_format and not compare_ids and not arguments2.get("video_id"):
    arguments2["video_id"] = prompt("Video", "Paste Your Video ID or Youtube Link > ")

if arguments2.get("channel_id"):
    arguments2["channel_id"] = extract_channel_id(arguments2["channel_id"])
if arguments2.get("video_id"):
    arguments2["video_id"] = extract_video_id(arguments2["video_id"])

options = {
    "channel_id": arguments2.get("channel_id"),
    "compare": compare_ids,
    "video_id": arguments2.get("video_id"),
    "sleep_time": sleep_time,
    "log_mode": log_mode,
    "latest_video": latest_video,
    "log_selection": log_selection,
    "history_path": history_path,
    "snapshot_time": snapshot_time,
    "history_hours": history_hours,
    "dashboard": dashboard_mode,
    "export_format": export_format,
    "export_path": export_path,
}
