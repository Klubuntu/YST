import os
import sys

from colorama import Fore, Style, init as init_colors

init_colors()

sep = "======================================================================"
soft_dir = os.path.join(os.getcwd(), "txt")

API_URL = "https://www.googleapis.com/youtube/v3"
REQUEST_TIMEOUT = 10
API_KEY = os.environ.get("YOUTUBE_API_KEY", "AIzaSyBGX0yQtfRPu9CRBEC4mZ95fnvNj00msik")

# default arguments
sleep_time = 2
logmode = False
get_latest_video = False

# history storage
DEFAULT_DB_PATH = "data/yst.db"


def ensure_output_dir():
    try:
        os.makedirs(soft_dir, exist_ok=True)
    except OSError as e:
        print(f"{Fore.LIGHTRED_EX}Cannot create output folder '{soft_dir}': {e}{Style.RESET_ALL}")
        sys.exit(1)
    return soft_dir