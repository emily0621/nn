import os
import tensorflow as tf
from tensorflow import cast, float32, shape, pad, transpose
import tensorflow as tf
from model import load, decode_batch_predictions
from configuration import PROJECT_ROOT
from keras.models import load_model
from configuration import PADDING_TOKEN, BATCH_SIZE
from process_dataset import get_test_dataset, get_form_dataset
import keras
from tensorflow import cast, shape, ones, gather, where, math, transpose
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
from process_dataset import get_num_to_char

IMAGE_WIDTH = 128
IMAGE_HEIGHT = 32


def distortion_free_resize(image, img_size):
    w, h = img_size
    image = tf.image.resize(image, size=(h, w), preserve_aspect_ratio=True)

    pad_height = h - shape(image)[0]
    pad_width = w - shape(image)[1]

    if pad_height % 2 != 0:
        height = pad_height // 2
        pad_height_top = height + 1
        pad_height_bottom = height
    else:
        pad_height_top = pad_height_bottom = pad_height // 2

    if pad_width % 2 != 0:
        width = pad_width // 2
        pad_width_left = width + 1
        pad_width_right = width
    else:
        pad_width_left = pad_width_right = pad_width // 2

    image = pad(
        image,
        paddings=[
            [pad_height_top, pad_height_bottom],
            [pad_width_left, pad_width_right],
            [0, 0],
        ],
    )

    image = transpose(image, perm=[1, 0, 2])
    image = tf.image.flip_left_right(image)
    return image


def preprocess_image(image_path):
    image = tf.io.read_file(image_path)
    image = tf.image.decode_png(image, 1)
    image = distortion_free_resize(image, (IMAGE_WIDTH, IMAGE_HEIGHT))
    image = cast(image, float32) / 255.0
    return image


image_path = 'D:\\lpnu3\\nn\\project\\words\\iam_words\\words\\a01\\a01-000u\\a01-000u-00-01.png'
image = preprocess_image(image_path)
model = load()
dataset = get_test_dataset()

form_name = 'a01-003'



