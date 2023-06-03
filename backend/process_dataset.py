import os
import numpy as np
from keras.layers import StringLookup
from configuration import PATH_TO_IMAGES, IMAGE_WIDTH, IMAGE_HEIGHT, BATCH_SIZE, PATH_TO_FORMS, PATH_TO_SENTENCES_IMAGES, \
    PATH_TO_SAVED_FOLDER, PADDING_TOKEN, PATH_TO_TEMP
import tensorflow as tf
import pickle

test_data, symbol_by_num, num_by_symbol, max_len, forms = None, None, None, None, {}
test_dataset = None


def preprocess_image(image_path, img_size=(IMAGE_WIDTH, IMAGE_HEIGHT)):
    image = tf.io.read_file(image_path)
    image = tf.image.decode_png(image, 1)

    w, h = img_size
    image = tf.image.resize(image, size=(h, w), preserve_aspect_ratio=True)

    pad_height = h - tf.shape(image)[0]
    pad_width = w - tf.shape(image)[1]

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

    image = tf.pad(image, paddings=[[pad_height_top, pad_height_bottom], [pad_width_left, pad_width_right], [0, 0]])

    image = tf.transpose(image, perm=[1, 0, 2])
    image = tf.image.flip_left_right(image)

    image = tf.cast(image, tf.float32) / 255.0
    return image


def label_to_vector(label):
    global num_by_symbol, max_len
    label = num_by_symbol(tf.strings.unicode_split(label, input_encoding="UTF-8"))
    length = tf.shape(label)[0]
    pad_amount = max_len - length
    label = tf.pad(label, paddings=[[0, pad_amount]], constant_values=PADDING_TOKEN)
    return label


def process_data(data):
    image = preprocess_image(data[0])
    label = label_to_vector(data[1])
    return {"image": image, "label": label, "path": data[0]}


def load_symbols():
    global symbol_by_num, num_by_symbol, max_len
    if symbol_by_num is None:
        with open(PATH_TO_SAVED_FOLDER + '\\symbols.pkl', 'rb') as file:
            data = pickle.load(file)
            symbols, max_len = data['symbols'], data['max_len']
        num_by_symbol = StringLookup(vocabulary=list(symbols), mask_token=None)
        symbol_by_num = StringLookup(vocabulary=num_by_symbol.get_vocabulary(), mask_token=None, invert=True)


def get_test_dataset():
    global test_data, test_dataset, max_len
    if test_dataset is None:
        load_symbols()
        test_data = np.load(PATH_TO_SAVED_FOLDER + 'test.npy')
        test_dataset = tf.data.Dataset.from_tensor_slices(test_data).map(process_data, num_parallel_calls=tf.data.AUTOTUNE)\
            .batch(BATCH_SIZE).cache().prefetch(tf.data.AUTOTUNE)
        return test_dataset
    else:
        return test_dataset


def get_symbol_by_num():
    global symbol_by_num, max_len
    return symbol_by_num, max_len


def load_forms(read=False):
    global forms
    if read:
        forms = {}
    if len(forms) == 0:
        try:
            with open(PATH_TO_SAVED_FOLDER + 'forms.pkl', 'rb') as file:
                forms = pickle.load(file)
        except FileNotFoundError:
            with open(PATH_TO_FORMS, "r") as file:
                for line in file:
                    if line[0] != '#':
                        form_name = line.split(' ')[0]
                        files = os.listdir(PATH_TO_SENTENCES_IMAGES)
                        matching_files = [file for file in files if file.startswith(form_name)]
                        forms[form_name] = matching_files
            with open(PATH_TO_SAVED_FOLDER + 'forms.pkl', 'wb') as file:
                pickle.dump(forms, file)
    return forms


def get_form_dataset(form_name):
    path_to_images = PATH_TO_IMAGES + '\\' + form_name.split('-')[0] + '\\' + form_name
    data = [(path_to_images + '\\' + name, 'label') for name in os.listdir(path_to_images)]
    dataset = tf.data.Dataset.from_tensor_slices(data).map(process_data, num_parallel_calls=tf.data.AUTOTUNE)
    return dataset.batch(BATCH_SIZE).cache().prefetch(tf.data.AUTOTUNE)


def read_own_handwriting():
    load_symbols()
    data = [(PATH_TO_TEMP + 'image.png', 'label')]
    dataset = tf.data.Dataset.from_tensor_slices(data).map(process_data, num_parallel_calls=tf.data.AUTOTUNE)
    return dataset.batch(BATCH_SIZE).cache().prefetch(tf.data.AUTOTUNE)


