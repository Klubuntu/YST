import sys
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

"""

Traceback (most recent call last):
  File "/home/programmer/OBS Data/Tools/YST2/YST.py", line 4, in <module>
    main()
  File "/home/programmer/OBS Data/Tools/YST2/YST_lib/main.py", line 81, in main
    request_video()
  File "/home/programmer/OBS Data/Tools/YST2/YST_lib/main.py", line 46, in request_video
    query2 = x = f'https://youtube.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={API_KEY}'
                                                                                        ^^^^^^^^
NameError: cannot access free variable 'video_id' where it is not associated with a value in enclosing scope

// python3 YST.py -channel_id=UCifZaTQPiHE2QRgEwDNfhug -video_id=wdHGVUiFGws

"""

if arguments:
    for arg_name, arg_value in arguments.items():
        try:
            if arg_name == "channel_id" and not used_channelID:
                channel_id = arg_value
                used_channelID = True
            elif arg_name == "video_id" and not used_videoID:
                video_id = arg_value
                used_videoID = True
        except:
            pass

    if not used_channelID:
        channel_query = input(f"{bcolors.BOLD}Paste Your Channel ID or Youtube Link > ")
        if len(channel_query) > 1:
            channel_id = channel_query.split("channel/")[1]
            used_channelID = True
        else:
            exit(f"{bcolors.FAIL}No Found Channel ID or Youtube Link{bcolors.DEFAULT}")

    if not used_videoID:
        video_query = input(f"{bcolors.BOLD}Paste Your Video ID or Youtube Link > ")
        if len(video_query) > 1:
            video_id = video_query.split("?v=")[1]
            used_videoID = True
        else:
            exit(f"{bcolors.FAIL}No Found Video ID or Youtube Link{bcolors.DEFAULT}")
# d = check_arg(1, "-channel_id")
# if (d == None):
#     try:
#       channel_query = input(f"{bcolors.BOLD}Paste Your Channel ID or Youtube Link > ")
#       if len(channel_query) > 1:
#         channel_id = channel_query.split("channel/")[1]
#         pass
#       else:
#         exit(f"{bcolors.FAIL}No Found Channel ID or Youtube Link{bcolors.DEFAULT}")
#     except:
#       channel_id = channel_query
# else:
#     channel_id = d
#     # channel_id = UC9QeWFl9wDaC3NH25v8VpgQ
# d = check_arg(2, "-video_id")
# if (d == None):
#     try:
#       video_query = input(f"{bcolors.BOLD}Paste Your Video ID or Youtube Link > ")
#       if len(video_query) > 1:
#         video_id = video_query.split("v=")[1]
#         pass
#       else:
#         exit(f"{bcolors.FAIL}No Found Channel ID or Youtube Link{bcolors.DEFAULT}")      
#       pass
#     except:
#       video_id = video_query
# else:
#     video_id = d
#     # video_id = OyWhdZZkEtY

# d = check_arg(3, "-sleep_time")
# if (d == None):
#     pass
# else:
#     try:
#       sleep_time = int(d)
#     except ValueError:
#       exit(f"{bcolors.FAIL}Invalid Number{bcolors.DEFAULT}")
#     except Exception:
#       exit(f"{bcolors.FAIL}Other error{bcolors.DEFAULT}") 

# d = check_arg(4, "-log_mode")
# if (d == None):
#     pass
# else:
#     try:
#       logmode = bool(d)
#     except ValueError:
#       exit(f"{bcolors.FAIL}Invalid value True/False{bcolors.DEFAULT}")
#     except Exception:
#       exit(f"{bcolors.FAIL}Other error{bcolors.DEFAULT}")

# d = check_arg(5, "-get_latest_video")
# if (d == None):
#     pass
# else:
#     try:
#       get_latest_video = bool(d)
#     except ValueError:
#       exit(f"{bcolors.FAIL}Invalid value True/False{bcolors.DEFAULT}")
#     except Exception:
#       exit(f"{bcolors.FAIL}Other error{bcolors.DEFAULT}")