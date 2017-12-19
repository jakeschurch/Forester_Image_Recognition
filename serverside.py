#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Purpose: Be able to use robot for image recognition techniques.

    Send images to server that does recognition for forester.

    - rpc -> remote procedure call: use rpyc package

server-side:
    rpyc sets server-sideon client side create connection to localhost given
    ip address of robot
    access imports module os and calls os functions

-- Project TODO's:
DONE: Set up image recognition model to work starting with laptop
DONE: Download fswebcam on distro.
DONE: Set up tether between laptop and forester.
DONE: Set up rpyc instance between laptop and forester.
DONE: Implement image recognition model using rpyc instance on forester.
"""

__author__ = "Jake Schurch"

import os
import sys
import math
os.chdir('/home/jake/Code/PythonEnvs/Forester_Image_Recognition/tensorflow')
utilPath = os.path.join(os.getcwd(), 'research/object_detection')
sys.path.append(utilPath)

import tarfile
import urllib.request
from matplotlib import pyplot as plt
import tensorflow as tf
import numpy as np
from PIL import Image
from utils import label_map_util
from utils import visualization_utils as vis_util
import rpyc

NUM_CLASSES = 90
TEST_IMAGE_DIR = '/home/jake/Code/PythonEnvs/Forester_Image_Recognition/Sent_Photos'
IMAGE_SIZE = (12, 8)


def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(
        np.uint8)


def _LoadImages():
    image_file_paths = []

    for root, dirs, filenames, in os.walk(TEST_IMAGE_DIR):
        for f in filenames:
            if '.jpg' in f:
                image_file_paths.append(os.path.join(TEST_IMAGE_DIR, f))
    return image_file_paths


class Model(object):
    def __init__(self):
        self.BaseURL = "http://download.tensorflow.org/models/object_detection"
        self.Graph = "frozen_inference_graph.pb"
        self.ModelName = "ssd_inception_v2_coco_11_06_2017"
        self.ModelFile = self.ModelName + ".tar.gz"
        self.Labels = os.path.join(utilPath, 'data', 'mscoco_label_map.pbtxt')

    def Download(self):
        """Download imagenet model from web."""

        FullURL = self.BaseURL + "/" + self.ModelFile
        opener = urllib.request.URLopener()
        opener.retrieve(FullURL, self.ModelFile)
        print("Has been downloaded")

        tar_file = tarfile.open(self.ModelFile)

        for file in tar_file.getmembers():
            file_name = os.path.basename(file.name)
            if self.Graph in file_name:
                tar_file.extract(file, os.getcwd())

        return True

    def GetCKPT_Path(self):
        CKPT_Path = os.path.join(os.getcwd(), self.ModelName, self.Graph)
        return CKPT_Path

    def GetLabelsPath(self):
        return self.Labels


def FindDetectedObjects(category_index, boxes, classes, scores, image_path,
                        object_wanted):
    '''NOTE: box array is ymin, xmin, ymax, xmax '''
    n_objects = 0
    sum_score = 0
    for (c, s, b) in zip(classes, scores, boxes):
        if s > .5 and category_index[c]['name'] == object_wanted:
            n_objects += 1
            sum_score += s
            angleToMove = FindAngle(b[1], b[3], b[0], b[2])

    image_num = image_path.split("image_")[1]
    image_num = image_num.split(".jpg")
    try:
        return image_num[0], sum_score / n_objects, angleToMove
    except ZeroDivisionError:
        return image_num[0], 0, 0


def FindAngle(xmin, xmax, ymin, ymax):
    xmid = (xmax + xmin) / 2
    ymid = (ymax + ymin) / 2
    if xmid > .60 or xmid < .40:
        angleToReturn = math.degrees(math.atan2((ymid - 0), (xmid - 0.5)))
        print("angle to return ", angleToReturn)
        return angleToReturn
    else:
        return 0


def RunObjectRecognitionModel():
    pathToCheck = os.path.join(os.getcwd(), Model().ModelName, Model().Graph)

    if not os.path.exists(pathToCheck):
        print("Downloading Model...please wait...")
        Model().Download()

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
        label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)

    TEST_IMAGE_PATHS = _LoadImages()

    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
            # Definite input and output Tensors for detection_graph
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            # Each box represents a part of the image where a particular object was detected.
            detection_boxes = detection_graph.get_tensor_by_name(
                'detection_boxes:0')
            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label
            detection_scores = detection_graph.get_tensor_by_name(
                'detection_scores:0')
            detection_classes = detection_graph.get_tensor_by_name(
                'detection_classes:0')
        num_detections = detection_graph.get_tensor_by_name('num_detections:0')

        return_dict = {}
        for image_n, image_path in enumerate(_LoadImages()):
            image = Image.open(image_path)
            # the array based representation of the image will be used later in
            # order to prepare the result image with boxes and labels on it.
            image_np = load_image_into_numpy_array(image)
            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)
            # Actual detection.
            (boxes, scores, classes, num) = sess.run(
                [
                    detection_boxes, detection_scores, detection_classes,
                    num_detections
                ],
                feed_dict={
                    image_tensor: image_np_expanded
                })

            img_number, avg_score, angle = FindDetectedObjects(
                category_index, np.squeeze(boxes), np.squeeze(classes),
                np.squeeze(scores), image_path, 'person')

            if avg_score > 0.0 or avg_score != 0:
                return_dict[img_number] = {"Score": avg_score, "Angle": angle}
            else:
                pass
            # Visualization of the results of a detection.
            # vis_util.visualize_boxes_and_labels_on_image_array(
            #     image_np,
            #     np.squeeze(boxes),
            #     np.squeeze(classes).astype(np.int32),
            #     np.squeeze(scores),
            #     category_index,
            #     use_normalized_coordinates=True,
            #     line_thickness=4)
            # plt.imshow(image_np)
            # plt.show()

        print(return_dict)
        return return_dict


RunObjectRecognitionModel()
