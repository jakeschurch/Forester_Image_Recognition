# -*- coding: UTF-8 -*-
"""
Purpose: Be able to use robot for image recognition techniques.

    Send images to server that does recognition for forester.
"""

__author__ = "Jake Schurch"

import os

SERVER_IP = "10.42.0.1"
LOCAL_PHOTO_PATH = "~/python/Photos"
REMOTE_PHOTO_DIR = "~/Code/PythonEnvs/Forester_Image_Recognition/Sent_Photos"


class Camera(object):
    def __init__(self):
        self.picnum = 0
        self.newest_photo_path = "{0}/image{1}.jpg".format(
            LOCAL_PHOTO_PATH, self.picnum)

    def TakePicture(self):
        os.system("fswebcam -r 352x288 -no-banner {0}/image_{1}.jpg".format(
            LOCAL_PHOTO_PATH, self.picnum))
        self.picnum += 1

    def SendPicture(self):
        os.system("scp {0} jake@{1}:{2}".format(self.newest_photo_path,
                                                SERVER_IP, REMOTE_PHOTO_DIR))


if __name__ == "__main__":
    import rypc

    cam = Camera()
    cam.TakePicture()
    cam.SendPicture()
    conn = rpyc.classic.connect(SERVER_IP, port=18888)
    conn.close()
