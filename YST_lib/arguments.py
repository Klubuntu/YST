import sys
import copy
from YST_lib.required import *

def check_arg():
    if len(sys.argv) > 1:
        args = {}
        for argument in sys.argv[1:]:
            if argument.startswith("-"):
                arg_parts = argument.split("=")
                if len(arg_parts) == 2:
                    arg_name = arg_parts[0][1:]
                    arg_value = arg_parts[1]
                    args[arg_name] = arg_value
        return args

arguments = check_arg()
arguments2 = copy.copy(arguments)

if arguments:
    for arg_name, arg_value in arguments.items():
        try:
            if arg_name == "channel_id" and not used_channelID:
                channel_id = arg_value
                used_channelID = True
            elif arg_name == "video_id" and not used_videoID:
                video_id = arg_value
                used_videoID = True
            elif arg_name == "latest_video" and not used_latestVideo:
                latest_video = arg_value
                used_latestVideo = True
        except:
            pass

    if not used_channelID:
        channel_query = input(f"{bcolors.BOLD}Paste Your Channel ID or Youtube Link > ")
        if len(channel_query) > 1:
            if "youtube.com/channel/" not in channel_query:
                arguments2['channel_id'] = channel_query
            else:
                arguments2['channel_id'] = channel_query.split("channel/")[1]
            used_channelID = True
        else:
            sys.exit(f"{bcolors.FAIL}No Found Channel ID or Youtube Link{bcolors.DEFAULT}")


    if 'latest_video' in arguments:
        used_videoID = True

    if not used_videoID:
        video_query = input(f"{bcolors.BOLD}Paste Your Video ID or Youtube Link > ")
        if len(video_query) > 1:
            if "?v=" not in video_query:
                arguments2['video_id'] = video_query
            else:
                arguments2['video_id'] = video_query.split("?v=")[1]
            used_videoID = True
        else:
            sys.exit(f"{bcolors.FAIL}No Found Video ID or Youtube Link{bcolors.DEFAULT}")
       