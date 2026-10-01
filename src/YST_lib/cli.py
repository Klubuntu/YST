import sys

import requests
from colorama import Fore, Style

TRUE_VALUES = ("1", "true", "yes", "on")


def parse_bool(value, default):
    if value is None:
        return default
    return value.strip().lower() in TRUE_VALUES


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


def check_arg(argv=None):
    args = {}
    for argument in sys.argv[1:] if argv is None else argv:
        if not argument.startswith("-") or "=" not in argument:
            continue
        name, _, value = argument[1:].partition("=")
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