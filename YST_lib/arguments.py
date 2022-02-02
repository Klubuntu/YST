import sys
from YST_lib.required import *

def check_arg(argument_num, argument_name):
    if len(sys.argv) > 1:
      if (sys.argv[argument_num].__contains__(argument_name)):
        x = sys.argv[argument_num].split("=")
        #print(x[1])
        arg1 = x[0]
        func = x[0] + "=" + x[1]
        return x[1]
      else:
        exit(f"{bcolors.FAIL}No Arguments{bcolors.DEFAULT}")


d = check_arg(1, "-channel_id")
if (d == None):
    try:
      channel_query = input(f"{bcolors.BOLD}Paste Your Channel ID or Youtube Link > ")
      if len(channel_query) > 1:
        channel_id = channel_query.split("channel/")[1]
        pass
      else:
        exit(f"{bcolors.FAIL}No Found Channel ID or Youtube Link{bcolors.DEFAULT}")
    except:
      channel_id = channel_query
else:
    channel_id = d
    # channel_id = UC9QeWFl9wDaC3NH25v8VpgQ
d = check_arg(2, "-video_id")
if (d == None):
    try:
      video_query = input(f"{bcolors.BOLD}Paste Your Video ID or Youtube Link > ")
      if len(video_query) > 1:
        video_id = video_query.split("v=")[1]
        pass
      else:
        exit(f"{bcolors.FAIL}No Found Channel ID or Youtube Link{bcolors.DEFAULT}")      
      pass
    except:
      video_id = video_query
else:
    video_id = d
    # video_id = OyWhdZZkEtY

d = check_arg(3, "-sleep_time")
if (d == None):
    pass
else:
    try:
      sleep_time = int(d)
    except ValueError:
      exit(f"{bcolors.FAIL}Invalid Number{bcolors.DEFAULT}")
    except Exception:
      exit(f"{bcolors.FAIL}Other errror{bcolors.DEFAULT}") 

d = check_arg(4, "-log_mode")
if (d == None):
    pass
else:
    try:
      logmode = bool(d)
    except ValueError:
      exit(f"{bcolors.FAIL}Invalid True/False{bcolors.DEFAULT}")
    except Exception:
      exit(f"{bcolors.FAIL}Other errror{bcolors.DEFAULT}")