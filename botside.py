#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Purpose: Be able to use robot for image recognition techniques.

    Send images to server that does recognition for forester.
"""

__author__ = "Jake Schurch"

from ev3dev.ev3 import *
import os
import robot
import time

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
        options = "-r 640x480 -fps 20 -S 5 -D 4 --set brightness=70% --no-banner"
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
    left = LargeMotor('outD')
    right = LargeMotor('outA')
    motors = [left, right]
    touch, null, null, null = robot.Sensors('touch', None, None, None)
    cam = Camera()
    conn = rpyc.classic.connect(SERVER_IP, port=18888)

    # Get Picture
    if angle != 0:
        left.run_timed(speed_sp=50, time_sp=3000)

    time.sleep(1)
    cam.TakePicture()
    rm_cmd = "rm {0}/*".format(REMOTE_PHOTO_DIR)
    conn.modules.os.system(rm_cmd)
    # conn.modules.os.system("workon tensorflow")
    cam.SendPicture()

    conn.modules.os.chdir(REMOTE_SCRIPT_DIR)
    out = conn.modules.serverside.RunObjectRecognitionModel()
    print(out)

    try:
        if out['0']["Score"] < .60:
            conn.close()
            RunProcess(angle=120)
        else:
            angleToMove = out['0']["Angle"]
            if angleToMove == 0:
                pass
            elif angleToMove > 90:
                angleToMove = angleToMove - 90
                print("moved left")
                left.run_timed(speed_sp=angleToMove, time_sp=3000)
                while left.state:
                    time.sleep(0.1)
            else:
                print("moved right")
                angleToMove = 90 - angleToMove
                right.run_timed(speed_sp=angleToMove, time_sp=3000)
                while right.state:
                    time.sleep(0.1)
            while not touch.value():
                for m in motors:
                    m.run_forever(speed_sp=-500)
            for m in motors:
                m.stop(stop_action="brake")

            [robot.Beep() for i in range(0, 4)]
    except KeyError:
        conn.close()
        RunProcess(angle=120)

    conn.close()


if __name__ == "__main__":
    RunProcess()
