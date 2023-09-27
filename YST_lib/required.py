from distutils.log import error
import requests
import json
import sys
import os
sys.path.append("..")
from lib.bcolors import *

sep = "======================================================================"
soft_dir = os.getcwd() + "//txt"
isExistDir = os.path.exists(soft_dir)
if not (isExistDir):
  os.makedirs(soft_dir)

# default arguments
sleep_time = 2
video_id = ""
channel_id = ""
channel_query = ""
used_channelID = False
used_videoID = False
get_latest_video = False
logmode = False

API_KEY = "AIzaSyBGX0yQtfRPu9CRBEC4mZ95fnvNj00msik"
