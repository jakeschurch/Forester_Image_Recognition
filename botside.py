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
        return "{0}/image{1}.jpg".format(LOCAL_PHOTO_PATH, self.picnum)

    def TakePicture(self):
        self.picnum = self.picnum + 1
        os.chdir(LOCAL_PHOTO_PATH)
        options = "-r 640x480 -S 3 -D 1 -F 2 --set brightness=70% --no-banner"
        cmd = "fswebcam {0} image_{1}.jpg".format(options, self.picnum)
        os.system(cmd)

    def SendPicture(self):
        cmd = "scp image_{0}.jpg jake@{1}:{2}".format(self.picnum, SERVER_IP,
                                                      REMOTE_PHOTO_DIR)
        os.system(cmd)

    def SendAllPictures(self):
        cmd = "scp ~/python/Photos/* jake@{0}:{1}".format(
            SERVER_IP, REMOTE_PHOTO_DIR)
        os.system(cmd)


def GetImages(camera, numPhotosToTake=3, angle=120):
    robot.Beep()

    for i in range(0, numPhotosToTake):
        camera.TakePicture()
        robot.Rotate(left, angle=angle)
    robot.Rotate(right, angle=(angle * numPhotosToTake))
    robot.Beep()


def FindBestChanceOfHuman(inDict):
    maxPercentage = 0
    iMaxPercentage = 0
    i = 0

    for k, v in inDict:
        for key, val in v:
            v[key] = val.strip("%").split(' ')
            if val[1] > maxPercentage:
                maxPercentage = val[1]
                iMaxPercentage = i
            i += 1
    return iMaxPercentage


def RunProcess():
    import rpyc
    global left
    global right

    left, right = robot.Motors('da')
    touch = robot.Sensors(one='touch')
    cam = Camera()
    angle = 120
    GetImages(cam, angle=angle)
    cam.SendAllPictures()

    conn = rpyc.classic.connect(SERVER_IP, port=18888)
    print("connected to server")
    conn.modules.os.chdir(REMOTE_SCRIPT_DIR)
    out = conn.modules.serverside.RunObjectRecognitionModel()

    iloc = FindBestChanceOfHuman(out)

    robot.Rotate(left, angle=(angle * iloc))

    while touch.value() is None:
        robot.Forward(left, right)
    robot.Backward(left, right)
    robot.Wait(0.5)
    robot.Off(left, right)


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
