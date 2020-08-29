from pymongo import MongoClient
from pymongo.collection import ObjectId
import bcrypt
from flask import Flask, request
import tensorflow.keras
from PIL import Image, ImageOps
from numpy import asarray
import numpy as np
import base64
import io
from imageio import imread
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
run_with_ngrok(app)

from flask_cors import CORS
import math
import json
from bson import ObjectId
import requests
CORS(app)
model = tensorflow.keras.models.load_model('model.h5')

client = MongoClient("mongodb+srv://user:pwd@cluster0.vswh5.mongodb.net/<dbname>?retryWrites=true&w=majority")

db = client.get_database("data")

def register(email, password):
    if db.users.find_one({"email":email}) == None:
        hashp = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        k = {"email":email, "password":hashp}
        db.users.insert_one(k)
        return {"status":"success"}
    else:
        return {"status":"failed"}

def login(email, password):
    k = db.users.find_one({"email":email})

    if k != None:
        x = bcrypt.hashpw(password.encode('utf-8'), k["password"])
        
        
        if x == k["password"]:
            return {"status":"success"}
        else:
            return {"status":"failed"}

    else:
        return {"status":"failed"}

def get_nearby(lat, lon, d, id):
    a = abs(float(d["geometry"]["location"]["lat"]) - lat)
    b = abs(float(d["geometry"]["location"]["lng"]) - lon)
    k = round(math.sqrt(a * a + b * b), 1)

    return {"id":id, "title":d["name"], "description":str(k) + " mi away", "image":d["icon"], "link":"https://www.google.com/search?q=" + d["name"], "maps":"https://www.google.com/maps/search/?api=1&query=" + str(lat) + "," + str(lon)}


def get_all(lat, lon):
    final = []
    x = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json?query=plant shop&radius=10000&key=AIzaSyB7L122E6_uJGXT6uheNw95q2cmrp7UClQ&location=" + str(lat) + "," + str(lon)).json()
    for i in range(1, 7):
        k = x["results"][i - 1]
        final.append(get_nearby(lat, lon, k, i))
    return {"first":final[0], "second":final[1], "third":final[2], "fourth":final[3], "fifth":final[4], "sixth":final[5]}


def predict(string):
    image = imread(io.BytesIO(base64.b64decode(string)))
    image = Image.open('test.jpg')
    image = ImageOps.fit(image, (224, 224), Image.ANTIALIAS)
    final_data = data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data = asarray(image)
    data = data.astype("float32")
    data /= 255.0
    final_data[0] = data
    diseases = [['Apple', 'Apple scab'], ['Apple', 'Black rot'], ['Apple', 'Cedar apple rust'], ['Apple', 'healthy'], ['Blueberry', 'healthy'], ['Cherry_(including_sour)', 'healthy'], ['Cherry_(including_sour)', 'Powdery mildew'], ['Corn_(maize)', 'Cercospora leaf spot Gray leaf spot'], ['Corn_(maize)', 'Common rust '], ['Corn_(maize)', 'healthy'], ['Corn_(maize)', 'Northern Leaf Blight'], ['Grape', 'Black rot'], ['Grape', 'Esca (Black Measles)'], ['Grape', 'healthy'], ['Grape', 'Leaf blight (Isariopsis Leaf Spot)'], ['Orange', 'Haunglongbing (Citrus greening)'], ['Peach', 'Bacterial spot'], ['Peach', 'healthy'], ['Pepper,_bell', 'Bacterial spot'], ['Pepper,_bell', 'healthy'], ['Potato', 'Early blight'], ['Potato', 'healthy'], ['Potato', 'Late blight'], ['Raspberry', 'healthy'], ['Soybean', 'healthy'], ['Squash', 'Powdery mildew'], ['Strawberry', 'healthy'], ['Strawberry', 'Leaf scorch'], ['Tomato', 'Bacterial spot'], ['Tomato', 'Early blight'], ['Tomato', 'healthy'], ['Tomato', 'Late blight'], ['Tomato', 'Leaf Mold'], ['Tomato', 'Septoria leaf spot'], ['Tomato', 'Spider mites Two-spotted spider mite'], ['Tomato', 'Target Spot'], ['Tomato', 'Tomato mosaic virus'], ['Tomato', 'Tomato Yellow Leaf Curl Virus']]
    pred = list(model.predict(final_data)[0])

    return(diseases[pred.index(max(pred))])


@app.route('/register', methods=["GET", "POST"])
def register_endpoint():
    data = request.json

    return register(data["email"], data["password"])

@app.route('/login', methods=["GET", "POST"])
def login_endpoint():
    data = request.json

    return login(data["email"], data["password"])

@app.route('/maps', methods=["GET", "POST"])
def maps_endpoint():
    data = request.json

    return get_all(float(data["lat"]), float(data["lon"]))

@app.route('/predict', methods=["GET", "POST"])
def predict_endpoint():
    data = request.json

    k = predict(data["input"])

    return {"plant":k[0], "disease":k[1]}

if __name__ == "__main__":
    app.run()
