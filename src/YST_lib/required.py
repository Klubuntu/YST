import os
import sys

from colorama import Fore, Style, init as init_colors

init_colors()


def load_env_file(path=".env"):
    if not os.path.isfile(path):
        return {}
    loaded = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                loaded[key.strip()] = value.strip().strip("'\"")
    except OSError:
        return {}
    return loaded


def apply_env(path=".env"):
    for key, value in load_env_file(path).items():
        os.environ.setdefault(key, value)


apply_env()

sep = "======================================================================"
soft_dir = os.path.join(os.getcwd(), "txt")

API_URL = "https://www.googleapis.com/youtube/v3"
REQUEST_TIMEOUT = 10
DEFAULT_API_KEY = "AIzaSyBGX0yQtfRPu9CRBEC4mZ95fnvNj00msik"
API_KEY = os.environ.get("YOUTUBE_API_KEY") or DEFAULT_API_KEY
API_KEY_SOURCE = ".env" if os.environ.get("YOUTUBE_API_KEY") else "built-in"

# default arguments
sleep_time = 2
logmode = False
get_latest_video = False

# history storage and export
DEFAULT_DB_PATH = "data/yst.db"
EXPORT_FOLDER = "exports"
EXPORT_FORMATS = ("csv", "json")

# API server
DEFAULT_SERVE_HOST = "127.0.0.1"
DEFAULT_SERVE_PORT = 9132


def ensure_output_dir():
    try:
        os.makedirs(soft_dir, exist_ok=True)
    except OSError as e:
        print(f"{Fore.LIGHTRED_EX}Cannot create output folder '{soft_dir}': {e}{Style.RESET_ALL}")
        sys.exit(1)
    return soft_dir


def env_default(name, fallback):
    """Read a setting from the environment, .env included."""
    value = os.environ.get(name)
    if value is None or not str(value).strip():
        return fallback
    return str(value).strip()