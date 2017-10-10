"""
Purpose: Be able to use robot for image recognition techniques.

- possibly use tensorflow's image recognition model using imagenet

Two possibilities:

1. take photos in all directions - do analysis for object, go closest
to that object

2. send images to server that does recognition for forester.
"""

__author__ = "Jake Schurch"
__version__ = "0.0.1a"

import tensorflow as tf
import fswebcam as fs
