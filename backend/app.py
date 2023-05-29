from flask import Flask, jsonify
from flask_cors import CORS
from process_dataset import get_test_dataset, load_forms
from configuration import PATH_TO_SENTENCES_IMAGES
from model import predict, predict_form
import random
import base64

app = Flask(__name__)
CORS(app)


@app.route('/predict', methods=['GET'])
def predict_text():
    dataset = get_test_dataset()
    image, predicted_label, label = predict(dataset)
    with open(image, 'rb') as image_file:
        image_data = image_file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
    response = jsonify({'image': image_base64, 'predicted_label': predicted_label, 'label': label})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:4200')
    return response


@app.route('/random_form', methods=['GET'])
def random_form():
    forms = load_forms()
    random_form = random.choice(list(forms.keys()))
    images = []
    for image in forms[random_form]:
        with open(PATH_TO_SENTENCES_IMAGES + image, "rb") as image_file:
            images.append(base64.b64encode(image_file.read()).decode("utf-8"))
    text = predict_form(random_form)
    response = jsonify({'images': images, 'text': text})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:4200')
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
