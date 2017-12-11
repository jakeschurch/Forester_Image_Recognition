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
    global left
    global right

    for i in range(0, numPhotosToTake):
        camera.TakePicture()
        robot.Rotate(left, angle=angle)
        robot.Wait(2)

    robot.Rotate(right, angle=(angle * numPhotosToTake))
    robot.Beep()


def FindBestChanceOfHuman(inDict):
    maxPercentage = 0
    MaxPercentageLoc = 0
    i = 0

    for key, val in inDict.items():
        for k, v in val.items():
            print("v: ", v)
            if v > maxPercentage:
                maxPercentage = v
                MaxPercentageLoc = i
            i += 1
    return MaxPercentageLoc, maxPercentage


def RunProcess(numPhotosToTake=3, angle=120):
    import rpyc

    global left
    global right

    left, right = robot.Motors('da')
    touch = robot.Sensors(one='touch')
    cam = Camera()
    GetImages(cam, angle=angle)
    conn = rpyc.classic.connect(SERVER_IP, port=18888)

    rm_cmd = "rm {0}/*".format(REMOTE_PHOTO_DIR)
    conn.modules.os.system(rm_cmd)
    cam.SendAllPictures()

    print("connected to server")
    conn.modules.os.chdir(REMOTE_SCRIPT_DIR)
    out = conn.modules.serverside.RunObjectRecognitionModel()

    iloc, highestChance = FindBestChanceOfHuman(out)

    if highestChance < .70:
        RunProcess(numPhotosToTake=numPhotosToTake + 1, angle=angle + 10)
    else:
        robot.Rotate(left, angle=(angle * iloc))

        while not touch.value():
            robot.Forward(left, right)
        robot.Backward(left, right)
        robot.Wait(0.5)
        robot.Off(left, right)
        robot.Beep()


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
