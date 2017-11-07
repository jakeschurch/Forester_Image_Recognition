
# -*- coding: UTF-8 -*-
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

__author__ = "Jake Schu`rch"
__version__ = "0.0.1a"

import os
import tarfile
import urllib.request
from matplotlib import pyplot as plt
import tensorflow as tf
import numpy as np
from PIL import Image
from utils import label_map_util
from utils import visualization_utils as vis_util
# import rpyc

NUM_CLASSES = 90
TEST_IMAGE_DIR = os.path.join(os.getcwd(), 'test_images')
IMAGE_SIZE = (12, 8)


def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)


def _LoadImages() -> list:
    image_file_paths = []

    for root, dirs, filenames, in os.walk(TEST_IMAGE_DIR):
        for f in filenames:
            print(f)
            if '.jpg' in f:
                image_file_paths.append(os.path.join(TEST_IMAGE_DIR, f))
    return image_file_paths


class Camera(object):

    def __init__(self):
        self.picnum = 0

    def TakePicture(self):
        try:
            os.system(
                "fswebcam -r 352x288 -no-banner image_{0}.jpg".format(
                    self.picnum
                ))
            self.picnum += 1
        except OSError:
            Exception("Not valid.")


class Model(object):

    def __init__(self):
        self.BaseURL = "http://download.tensorflow.org/models/object_detection/"
        self.Graph = "frozen_inference_graph.pb"
        self.ModelName = "ssd_inception_v2_coco_11_06_2017"
        self.ModelFile = self.ModelName + ".tar.gz"
        self.Labels = os.path.join('data', 'mscoco_label_map.pbtxt')

    def Download(self):
        """Download imagenet model from web."""

        FullURL = self.BaseURL + self.ModelFile
        opener = urllib.request.URLopener()
        opener.retrieve(FullURL, self.ModelFile)
        print("Has been downloaded")

        tar_file = tarfile.open(self.ModelFile)

        for file in tar_file.getmembers():
            file_name = os.path.basename(file.name)
            if self.Graph in file_name:
                tar_file.extract(file, os.getcwd())

    def GetCKPT_Path(self):
        CKPT_Path = os.path.join(os.getcwd(), self.ModelName, self.Graph)
        return CKPT_Path

    def GetLabelsPath(self):
        return self.Labels


GraphPath = Model().GetCKPT_Path()

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(GraphPath, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

LabelsPath = Model().GetLabelsPath()
label_map = label_map_util.load_labelmap(LabelsPath)
categories = label_map_util.convert_label_map_to_categories(
    label_map, max_num_classes=NUM_CLASSES,
    use_display_name=True
)
category_index = label_map_util.create_category_index(categories)
TEST_IMAGE_PATHS = _LoadImages()
IMAGE_SIZE = (12, 8)

i = 0
with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
        # Definite input and output Tensors for detection_graph
        image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        detection_boxes = detection_graph.get_tensor_by_name(
            'detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        detection_scores = detection_graph.get_tensor_by_name(
            'detection_scores:0')
        detection_classes = detection_graph.get_tensor_by_name(
            'detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')
    for image_path in _LoadImages():
        image = Image.open(image_path)
        # the array based representation of the image will be used later in order to prepare the
        # result image with boxes and labels on it.
        image_np = load_image_into_numpy_array(image)
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image_np, axis=0)
        # Actual detection.
        (boxes, scores, classes, num) = sess.run(
            [detection_boxes, detection_scores,
                detection_classes, num_detections],
            feed_dict={image_tensor: image_np_expanded})
        # Visualization of the results of a detection.
        vis_util.visualize_boxes_and_labels_on_image_array(
            image_np,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            category_index,
            use_normalized_coordinates=True,
            line_thickness=8)
        plt.savefig('fig{0}.png'.format(i), figsize=IMAGE_SIZE)
        i += 1
        plt.imshow(image_np)
