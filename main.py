import json
from functools import wraps
from flask import Flask, request, jsonify
from flask import  make_response
from flask_cors import CORS

import tensorflow as tf
from PIL import Image
from numpy import asarray
import numpy as np
import uuid
import os

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})

Models = {}


# read the config.json file
with open('config.json') as config_file:
    config = json.load(config_file)

    # for every model inside the models list create a tflite instance and allocate the tensors
    for model in config['models']:
        Models[model['endpoint']] = tf.lite.Interpreter(
            model_path=model['model'])
        Models[model['endpoint']].allocate_tensors()




@app.route('/')
def index():
    return 'It\'s working!'

# creating route for getting the available models

USERNAME = "admin"
PASSWORD = "admin"

# Function to check the provided username and password
def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

# Function to return a 401 Unauthorized response
def unauthorized():
    return make_response("Unauthorized", 401, {"WWW-Authenticate": 'Basic realm="Login Required"'})

# Decorator to require authentication for a route
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return unauthorized()
        return f(*args, **kwargs)
    return decorated


@app.route('/models', methods=['GET'])
def get_models():

    # read the config.json file
    with open('config.json') as json_file:
        data = json.load(json_file)

        # remove the model key inside the models array
        for model in data['models']:
            model.pop('model', None)

        return jsonify(data)


# create a predict route with a query parameter for the model name
@app.route('/predict/<model_name>', methods=['POST'])

def predict(model_name):

    # return error if the model does not exist
    if model_name not in Models:
        result = {
            'error': 'Model does not exist',
            'description': 'The model you are trying to use does not exist. Please check the available models using the /models endpoint'
        }
        return jsonify(result)

    # get the model from the models dictionary
    model = Models[model_name]
    print(model)
    # get the image from the request and save it inside the images folder
    file = request.files['image']
    extension = os.path.splitext(file.filename)[1]
    filename = str(uuid.uuid4()) + extension
    file.save('./image/' + filename)
    image = Image.open('./image/' + filename)

    # resizing and reshaping the image
    image = image.resize((224, 224))
    image = np.array(np.expand_dims(image, axis=0), dtype='float32')

    # get the input and output tensors
    input_details = model.get_input_details()
    output_details = model.get_output_details()

    # set the input tensor and invoke the interpreter
    model.set_tensor(input_details[0]['index'], image)
    model.invoke()

    # get the output tensor and convert it to a list
    output_data = model.get_tensor(output_details[0]['index'])
    predictions = output_data[0].tolist()

    # delete the image from the images folder
    os.remove('./image/' + filename)

    # generate the result
    result = {
        'result': predictions,
        
    }
    return jsonify(result), 200


if __name__ == '__main__':
    app.run(debug=True)
