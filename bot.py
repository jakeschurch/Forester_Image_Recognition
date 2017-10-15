"""
Purpose: Be able to use robot for image recognition techniques.

- possibly use tensorflow's image recognition model using imagenet

Two possibilities:

1. take photos in all directions - do analysis for object, go closest
to that object

2. send images to server that does recognition for forester.

-send images to server - rpc -> remote procedure call: use rpyc package

server-side:
    rpyc sets server-sideon client side create connection to localhsost given ip
        address of robot
    access imports module os and calls os functions

intermediary file for photos?

laptop as part of the robot?

-- Project TODO's:
TODO: Set up image recognition model to work starting with laptop
TODO: Set up tether between laptop and forester. NOTE: may want to use bash.
TODO: Set up rpyc instance between laptop and forester.
TODO: Implement image recognition model using rpyc instance on forester.
"""

__author__ = "Jake Schurch"
__version__ = "0.0.1a"

import tensorflow as tf
import rpyc
import os
import tarfile
import urllib


class Camera(object):
    picnum = 0

    def __init__(self):
        pass

    def TakePicture(self):
        try:
            os.system(f"fswebcam -r 352x288 -no-banner {picnum}.jpg")
            self.picnum += 1
        except OSError:
            Exception("Not valid.")


class Model(object):

    def __init__(self, framework: str):
        if "server" in framework:
            self.InitModel
        else:
            pass

    def InitModel(self):
        ModelBaseURL = "http://download.tensorflow.org/models/object_detection"
        ModelFile = "ssd_inception_v2_coco_11_06_2017.tar.gz"
        FullURL = ModelBaseURL + "/" + ModelFile

        if not os.path.exists(f"/{ModelName}"):
            os.system(f"wget -O {FullURL}")
            tar_file = tarfile.open(ModelFile)

            # Load Frozen Model
            for file in tar_file.getmembers():
                if "frozen_inference_graph.pb" in file.name:
                    tar_file.extract(file, os.getcwd())

        def SetToActive(self):



if __name__ == "__main__":
    pass
