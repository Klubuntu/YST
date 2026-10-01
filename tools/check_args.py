import os
import sys

sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src")
)

from YST_lib.cli import check_arg

arguments = check_arg()

if not arguments:
    print("No arguments provided")
else:
    for name, value in arguments.items():
        print(f"{name}: {value}")