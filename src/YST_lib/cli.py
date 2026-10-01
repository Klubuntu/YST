import re
import sys
from datetime import datetime, timezone

import requests
from colorama import Fore, Style

TRUE_VALUES = ("1", "true", "yes", "on")

STAT_FILES = {
    "subs": "channel_subscribers.txt",
    "channel_views": "channel_viewsCount.txt",
    "channel_videos": "channel_videoCount.txt",
    "video_views": "video_views.txt",
    "video_likes": "video_likes.txt",
    "video_comments": "video_comments.txt",
}

STAT_ALIASES = {
    "subscriber_count": "subs",
    "subscribers": "subs",
    "channel_subscribers": "subs",
    "channel_views_count": "channel_views",
    "channel_view_count": "channel_views",
    "channel_videocount": "channel_videos",
    "channel_video_count": "channel_videos",
    "videos": "channel_videos",
    "views": "video_views",
    "likes": "video_likes",
    "comments": "video_comments",
}


API_ERRORS = {
    "keyInvalid": "The API key is invalid. Set YOUTUBE_API_KEY in .env or your environment.",
    "quotaExceeded": "The daily API quota is spent. Try again after midnight UTC.",
    "dailyLimitExceeded": "The daily API quota is spent. Try again after midnight UTC.",
    "forbidden": "The API key is not allowed to use this resource.",
    "accessNotConfigured": "The YouTube Data API is not enabled for this key.",
    "rateLimitExceeded": "Too many requests, slowing down. Raise -sleep_time.",
}


def _error_details(payload):
    error = (payload.get("error") or {}) if isinstance(payload, dict) else {}
    reasons = []
    for item in error.get("errors") or []:
        if isinstance(item, dict) and item.get("reason"):
            reasons.append(item["reason"])
    for detail in error.get("details") or []:
        if isinstance(detail, dict) and detail.get("reason"):
            reasons.append(detail["reason"])
    if error.get("status"):
        reasons.append(error["status"])
    return reasons, error.get("message") or ""


def api_error_message(response, payload):
    reasons, message = _error_details(payload)

    haystack = " ".join(reasons + [message]).lower()
    if "key_invalid" in haystack or "api key not valid" in haystack or "apikey" in haystack:
        return API_ERRORS["keyInvalid"]
    if "quota" in haystack:
        return API_ERRORS["quotaExceeded"]
    if "rate limit" in haystack or "ratelimit" in haystack:
        return API_ERRORS["rateLimitExceeded"]
    if "accessnotconfigured" in haystack.replace("_", ""):
        return API_ERRORS["accessNotConfigured"]

    for reason in reasons:
        if reason in API_ERRORS:
            return API_ERRORS[reason]

    if response.status_code == 403:
        return "Access denied. Check the API key and its quota."
    if response.status_code == 404:
        return "Not found. Check the channel or video ID."
    if message:
        return message
    return f"Request failed with HTTP {response.status_code}."


def parse_bool(value, default):
    if value is None:
        return default
    return value.strip().lower() in TRUE_VALUES


def normalize_stat(name):
    key = name.strip().lower().replace("-", "_").replace(" ", "_")
    key = STAT_ALIASES.get(key, key)
    return key if key in STAT_FILES else None


def parse_stat_list(value):
    keys = []
    for name in re.split(r"[,\s]+", value or ""):
        if not name:
            continue
        key = normalize_stat(name)
        if key is None:
            sys.exit(
                f"{Fore.LIGHTRED_EX}Unknown metric '{name}'.{Style.RESET_ALL}\n"
                f"{Style.BRIGHT}Available: {Fore.YELLOW}{', '.join(STAT_FILES)}{Style.RESET_ALL}"
            )
        if key not in keys:
            keys.append(key)
    return keys


def resolve_log_selection(enable=None, disable=None):
    enabled = parse_stat_list(enable)
    disabled = parse_stat_list(disable)

    if enabled and disabled:
        sys.exit(
            f"{Fore.LIGHTRED_EX}Use either -enable_log or -disable_log, not both.{Style.RESET_ALL}"
        )
    if enabled:
        return set(enabled)
    return set(STAT_FILES) - set(disabled)


def parse_int(value, default, name="value"):
    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        print(f"{Fore.LIGHTYELLOW_EX}Invalid {name} '{value}', using {default}{Style.RESET_ALL}")
        return default
    if parsed < 1:
        print(f"{Fore.LIGHTYELLOW_EX}{name} must be 1 or more, using {default}{Style.RESET_ALL}")
        return default
    return parsed


SUBCOMMANDS = ("video", "channel", "latest", "monitor", "compare", "export")

SUBCOMMAND_HELP = """usage: yst <command> [options]

commands:
  video <ID>       track one video (channel is asked for)
  channel <ID>     track a channel with its latest video
  latest <ID>      same as channel, for the newest video
  monitor <ID>     channel monitoring with console output and deltas
  compare <ID...>  compare up to 50 videos side by side
  export <ID>      export the stored history to CSV and exit

Every command also accepts the regular options, for example:
  yst monitor UCifZaTQPiHE2QRgEwDNfhug -sleep_time=60 -dashboard=True
"""


def expand_subcommand(tokens):
    if not tokens or tokens[0] not in SUBCOMMANDS:
        return tokens

    command, rest = tokens[0], list(tokens[1:])
    if rest and rest[0].startswith("-"):
        sys.exit(
            f"{Fore.LIGHTRED_EX}'{command}' needs an ID, for example "
            f"'yst {command} UCifZaTQPiHE2QRgEwDNfhug'.{Style.RESET_ALL}"
        )

    prefix = {
        "video": [],
        "channel": ["-latest_video=True"],
        "latest": ["-latest_video=True"],
        "monitor": ["-latest_video=True", "-log_mode=True"],
        "compare": [],
        "export": ["-export=csv"],
    }[command]

    if command == "compare":
        return ["-compare", ",".join(rest), *prefix]
    if command == "video":
        return ["-video_id", rest[0], *rest[1:], *prefix]
    if command == "export":
        return ["-channel_id", rest[0], *rest[1:], *prefix]
    return ["-channel_id", rest[0], *rest[1:], *prefix]


def check_arg(argv=None):
    args = {}
    tokens = expand_subcommand(sys.argv[1:] if argv is None else argv)
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if not token.startswith("-"):
            continue
        name, separator, value = token[1:].partition("=")
        if not separator:
            values = []
            while index < len(tokens) and not tokens[index].startswith("-"):
                values.append(tokens[index])
                index += 1
            value = " ".join(values)
        if name:
            args[name] = value
    return args


def resolve_handle(name):
    from YST_lib.required import API_KEY, API_URL, REQUEST_TIMEOUT

    for parameter in ("forHandle", "forUsername"):
        query = f"{API_URL}/channels?part=id&{parameter}={name}&key={API_KEY}"
        try:
            items = requests.get(query, timeout=REQUEST_TIMEOUT).json().get("items") or []
        except (requests.RequestException, ValueError, AttributeError):
            items = []
        if items:
            return items[0].get("id")
    return None


def extract_channel_id(value):
    if value.startswith("UC"):
        return value

    for marker in ("/channel/", "/user/"):
        if marker in value:
            return value.split(marker)[1].split("/")[0].split("?")[0].split("&")[0]

    is_handle = value.startswith("@")
    if "/" not in value and not is_handle:
        return value

    resolved = resolve_handle(value.lstrip("@").rstrip("/").split("/")[-1])
    if not resolved:
        sys.exit(
            f"{Fore.LIGHTRED_EX}Could not resolve '{value}' to a Channel ID.{Style.RESET_ALL}\n"
            f"{Style.BRIGHT}Use the Channel ID instead: {Fore.YELLOW}UCxxxxxxxxxxxx{Style.RESET_ALL}"
        )
    return resolved


def extract_video_id(value):
    for marker in ("?v=", "youtu.be/", "/shorts/", "/live/", "/embed/"):
        if marker in value:
            return value.split(marker)[1].split("&")[0].split("/")[0]
    return value


def parse_duration(value):
    if not value:
        return None
    match = re.match(
        r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$", value.strip().upper()
    )
    if not match:
        return None
    hours, minutes, seconds = (int(part) if part else 0 for part in match.groups())
    return hours * 3600 + minutes * 60 + seconds


def format_duration(seconds):
    if not seconds:
        return "unknown"
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def parse_published_at(value):
    if not value:
        return None
    try:
        moment = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return int(moment.timestamp())