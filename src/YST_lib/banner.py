from colorama import Fore, Style

BANNER = r"""__  _____________
 \ \/ / ___/_  __/
  \  /\__ \ / /
  / /___/ // /
 /_//____//_/"""


def print_banner(color=Fore.CYAN):
    for line in BANNER.splitlines():
        print(f"{color}{line}{Style.RESET_ALL}")
