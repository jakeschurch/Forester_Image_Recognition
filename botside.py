#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Purpose: Be able to use robot for image recognition techniques.

    Send images to server that does recognition for forester.
"""

__author__ = "Jake Schurch"

import os

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
        cmd = "fswebcam -r 640x480 --set brightness=90% --no-banner image_{0}.jpg".format(self.picnum)
        os.system(cmd)

    def SendPicture(self):
        cmd = "scp image_{0}.jpg jake@{1}:{2}".format(self.picnum,
                                            SERVER_IP, REMOTE_PHOTO_DIR)
        os.system(cmd)


if __name__ == "__main__":
    import rpyc

    cam = Camera()
    cam.TakePicture()
    cam.SendPicture()
    conn = rpyc.classic.connect(SERVER_IP, port=18888)
    print("connected to server")
    conn.modules.os.system("workon tensorflow")
    print("working on tensorflow")
    conn.modules.os.chdir(REMOTE_SCRIPT_DIR)
    conn.modules.os.system("python3 serverside.py")
    conn.close()
