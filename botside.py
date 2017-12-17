#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Purpose: Be able to use robot for image recognition techniques.

    Send images to server that does recognition for forester.
"""

__author__ = "Jake Schurch"

import os
from ev3dev.ev3 import *
import robot

SERVER_IP = "10.42.0.1"
LOCAL_PHOTO_PATH = "/home/robot/python/Photos"
REMOTE_PHOTO_DIR = "/home/jake/Code/PythonEnvs/Forester_Image_Recognition/Sent_Photos"
REMOTE_SCRIPT_DIR = "/home/jake/Code/PythonEnvs/Forester_Image_Recognition/"


class Camera(object):
    def __init__(self):
        self.picnum = 0

    def GetPhotoPath(self):
        return "{0}/image_0.jpg".format(LOCAL_PHOTO_PATH)

    def TakePicture(self):
        os.chdir(LOCAL_PHOTO_PATH)
        options = "-r 640x480 -S 3 -D 1 -F 2 --set brightness=70% --no-banner"
        cmd = "fswebcam {0} image_0.jpg".format(options)
        os.system(cmd)

    def SendPicture(self):
        cmd = "scp image_0.jpg jake@{0}:{1}".format(SERVER_IP,
                                                    REMOTE_PHOTO_DIR)
        os.system(cmd)

    def SendAllPictures(self):
        cmd = "scp ~/python/Photos/* jake@{0}:{1}".format(
            SERVER_IP, REMOTE_PHOTO_DIR)
        os.system(cmd)


def RunProcess(angle=0):
    # Setup
    import rpyc
    global left
    global right
    left, right = robot.Motors('da')
    touch, null, null, null = robot.Sensors('touch', None, None, None)
    cam = Camera()
    conn = rpyc.classic.connect(SERVER_IP, port=18888)

    # Get Picture
    if angle != 0:
        robot.Rotate(left, angle)

    cam.TakePicture()
    # rm_cmd = "rm {0}/*".format(REMOTE_PHOTO_DIR)
    # conn.modules.os.system(rm_cmd)
    cam.SendPicture()

    conn.modules.os.chdir(REMOTE_SCRIPT_DIR)
    out = conn.modules.serverside.RunObjectRecognitionModel()
    print(out)

    if out['0']["Score"] < .70:
        conn.close()
        RunProcess(angle=120)
    else:
        robot.Rotate(left, angle=out["New Angle"])

        while not touch.value():
            [left, right].run_timed(speed_sp=500)

        robot.Shutdown(left, right)
        [robot.Beep() for i in range(0, 3)]

    conn.close()


if __name__ == "__main__":
    RunProcess()
    # import rpyc
    #
    # cam = Camera()
    # cam.TakePicture()
    # cam.SendPicture()
    # conn = rpyc.classic.connect(SERVER_IP, port=18888)
    # print("connected to server")
    # conn.modules.os.chdir(REMOTE_SCRIPT_DIR)
    # out = conn.modules.serverside.RunObjectRecognitionModel()
    # print(out, out)
    # #     object_dict = conn.modules.os.system("python3 serverside.py")
    # # print(object_dict)
    #
    # conn.close()
