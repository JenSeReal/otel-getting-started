import time
import requests
from flask import Flask, make_response
from client import FakerClient, ChaosClient

# global variables
app = Flask(__name__)

@app.route('/users', methods=['GET'])
def get_user():
    user, status = db.get_user(123)
    data = {}
    if user is not None:
        data = {
            "id": user.id,
            "name": user.name,
            "address": user.address
        }
    response = make_response(data, status)
    return response

def do_stuff():
    time.sleep(.1)
    url = "http://httpbin:80/anything"
    response = requests.get(url)

@app.route('/')
def index():
    do_stuff()
    current_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
    return f"Hello, World! It's currently {current_time}"

if __name__ == "__main__":
    db = ChaosClient(client=FakerClient())
    app.run(host="0.0.0.0", debug = True)