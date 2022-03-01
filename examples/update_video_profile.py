# -*- coding: utf-8 -*- 

#######################################
# Author: YinMo
# Source: https://github.com/DeachSword/CHRLINE/blob/master/examples/update_video_profile.py
# Version: 1.0.0
#######################################

from CHRLINE import *

token = input("Auth Token:")

if token == '':
    token = None

cl = CHRLINE(token)

video_path = input("Video Path:")
image_path = input("Image Path:")

cl.updateProfileImage(video_path) # the first step is to update the video
cl.updateProfileImage(image_path, type='vp') # that let server know u have updated the video

print("ok.")