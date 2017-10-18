"""
Purpose: Be able to use robot for image recognition techniques.

- possibly use tensorflow's image recognition model using imagenet

Two possibilities:

1. take photos in all directions - do analysis for object, go closest
to that object

2. send images to server that does recognition for forester.

-send images to server - rpc -> remote procedure call: use rpyc package

server-side:
    rpyc sets server-sideon client side create connection to localhost given
    ip address of robot
    access imports module os and calls os functions

intermediary file for photos?

laptop as part of the robot?

-- Project TODO's:
TODO: Set up image recognition model to work starting with laptop
REVIEW: Download fswebcam on debian distro.
TODO: Set up tether between laptop and forester. NOTE: may want to use bash.
TODO: Set up rpyc instance between laptop and forester.
TODO: Implement image recognition model using rpyc instance on forester.

QUESTION: Change file to bytestream?
QUESTION: Define folder paths for images and model?
"""

__author__ = "Jake Schurch"
__version__ = "0.0.1a"

import os
import tarfile
import urllib.request

# import rpyc
# import tensorflow as tf


class Camera(object):

    def __init__(self):
        self.picnum = 0

    def TakePicture(self):
        try:
            os.system(
                f"fswebcam -r 352x288 -no-banner image_{self.picnum}.jpg")
            self.picnum += 1
        except OSError:
            Exception("Not valid.")


class Model(object):

    def __init__(self):
        self.BaseURL = "http://download.tensorflow.org/models/object_detection"

        self.ModelFile = r"ssd_inception_v2_coco_11_06_2017.tar.gz"

    def Download(self) -> None:
        """Download imagenet model from web."""

        FullURL = self.BaseURL + "/" + self.ModelFile

        opener = urllib.request.URLopener()
        opener.retrieve(FullURL, self.ModelFile)

    def ExtractGraph(self) -> None:
        """Extract model from tar zip file."""

        tar_file = tarfile.open(ModelFile)
        for file in tar_file.getmembers():
            if "frozen_inference_graph.pb" in file.name:
                tar_file.extract(file, os.getcwd())

    def LoadGraph(self):
        return NotImplementedError

    def LoadLabels(self):
        return NotImplementedError


if __name__ == "__main__":
    m = Model()
    m.Download()
    m.Extract()
