from distutils.log import error
import requests
import json
import sys
import os
sys.path.append("..")
from lib.bcolors import *

from time import localtime, strftime, sleep


sep = "======================================================================"
soft_dir = os.getcwd() + "//YST_output"
isExistDir = os.path.exists(soft_dir)
if (isExistDir):
  pass
else:
  os.makedirs(soft_dir)

# default arguments
sleep_time = 2
video_id = ""
channel_id = ""
logmode = False

channel_query = ""
