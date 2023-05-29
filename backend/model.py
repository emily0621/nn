import random
from configuration import PATH_TO_SAVED_FOLDER
from keras.models import load_model
from configuration import PADDING_TOKEN
import keras
from tensorflow import cast, shape, ones, gather, where, math
import tensorflow as tf
import numpy as np
from process_dataset import get_form_dataset, get_symbol_by_num

model = None
predictions = {'images': [], 'predictions': [], 'labels': []}
current_batch = 1


class CTCLayer(keras.layers.Layer):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.loss_fn = keras.backend.ctc_batch_cost

    def call(self, y_true, y_pred):
        batch_len = cast(shape(y_true)[0], dtype="int64")
        input_length = cast(shape(y_pred)[1], dtype="int64")
        label_length = cast(shape(y_true)[1], dtype="int64")

        input_length = input_length * ones(shape=(batch_len, 1), dtype="int64")
        label_length = label_length * ones(shape=(batch_len, 1), dtype="int64")
        loss = self.loss_fn(y_true, y_pred, input_length, label_length)
        self.add_loss(loss)
        return y_pred


def load():
    global model
    if model is None:
        with keras.utils.custom_object_scope({'CTCLayer': CTCLayer}):
            model = load_model(f'{PATH_TO_SAVED_FOLDER}\\model.h5')


def decode_predictions(predictions):
    symbol_by_num, max_len = get_symbol_by_num()
    input_len = np.ones(predictions.shape[0]) * predictions.shape[1]
    results = keras.backend.ctc_decode(predictions, input_length=input_len, greedy=True)[0][0][:, :max_len]
    output_text = []
    for res in results:
        res = tf.gather(res, tf.where(tf.math.not_equal(res, -1)))
        res = tf.strings.reduce_join(symbol_by_num(res)).numpy().decode("utf-8")
        output_text.append(res)
    return output_text


def decode_labels(labels):
    symbol_by_num, max_len = get_symbol_by_num()
    decoded_labels = []
    for label in labels:
        label_without_padding = tf.gather(label, tf.where(tf.math.not_equal(label, PADDING_TOKEN)))
        decoded_labels.append(tf.strings.reduce_join(symbol_by_num(label_without_padding)).numpy().decode("utf-8"))
    return decoded_labels


def update_current_batch(dataset):
    global current_batch
    total_num_of_batches = tf.data.experimental.cardinality(dataset).numpy()
    if current_batch + 1 > total_num_of_batches:
        current_batch = 0
    else:
        current_batch += 1


def predict(dataset):
    global model, current_batch
    load()
    symbol_by_num, max_len = get_symbol_by_num()
    if len(predictions['images']) == 0:
        prediction_model = keras.models.Model(model.get_layer(name="image").input, model.get_layer(name="output").output)
        for data in dataset.take(current_batch):
            predictions['predictions'] = decode_predictions(prediction_model.predict(data['image']))
            predictions['labels'] = decode_labels(data['label'].numpy().tolist())
            predictions['images'] = data['path'].numpy().tolist()
        update_current_batch(dataset)
    idx = random.randint(0, len(predictions['images']) - 1)
    prediction = predictions['predictions'].pop(idx)
    image_path = predictions['images'].pop(idx).decode()
    label = predictions['labels'].pop(idx)
    return image_path, prediction, label


def predict_form(form_name):
    global model
    load()
    form_dataset = get_form_dataset(form_name)
    prediction_model = keras.models.Model(model.get_layer(name="image").input, model.get_layer(name="output").output)
    result = []
    for data in form_dataset:
        prediction = decode_predictions(prediction_model.predict(data['image']))
        result += prediction
    return ' '.join(result)
