#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Purpose: Be able to use robot for image recognition techniques.

    Send images to server that does recognition for forester.
"""

__author__ = "Jake Schurch"

import os
from ev3dev.ev3 import *

SERVER_IP = "10.42.0.1"
LOCAL_PHOTO_PATH = "/home/robot/python/Photos"
REMOTE_PHOTO_DIR = "/home/jake/Code/PythonEnvs/Forester_Image_Recognition/Sent_Photos"
REMOTE_SCRIPT_DIR = "/home/jake/Code/PythonEnvs/Forester_Image_Recognition/"


class Camera(object):
    def __init__(self):
        self.picnum = 0

    def GetPhotoPath(self):
        return "{0}/image{1}.jpg".format(LOCAL_PHOTO_PATH, self.picnum)

    def TakePicture(self):
        self.picnum = self.picnum + 1
        os.chdir(LOCAL_PHOTO_PATH)
        options = "-r 640x480 -S 3 -D 1 -F 5 --set brightness=70% --no-banner"
        cmd = "fswebcam {0} image_{1}.jpg".format(options, self.picnum)
        os.system(cmd)

    def SendPicture(self):
        cmd = "scp image_{0}.jpg jake@{1}:{2}".format(self.picnum, SERVER_IP,
                                                      REMOTE_PHOTO_DIR)
        os.system(cmd)


if __name__ == "__main__":
    import rpyc

    cam = Camera()
    cam.TakePicture()
    cam.SendPicture()
    conn = rpyc.classic.connect(SERVER_IP, port=18888)
    print("connected to server")
    conn.modules.os.chdir(REMOTE_SCRIPT_DIR)
    out = conn.modules.serverside.RunObjectRecognitionModel()
    print(out, out)
    #     object_dict = conn.modules.os.system("python3 serverside.py")
    # print(object_dict)

    conn.close()
