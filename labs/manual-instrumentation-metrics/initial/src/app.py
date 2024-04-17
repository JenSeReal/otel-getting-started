# pyright: reportMissingTypeStubs=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportAttributeAccessIssue=false

import time
import logging

import requests
from client import ChaosClient, FakerClient
from flask import Flask, make_response, request, Response
from metric_utils import create_meter, create_request_instruments

# global variables
app = Flask(__name__)
meter = create_meter("app.py", "0.1")

@app.before_request
def before_request_func():
    request.environ["request_start"] = time.time_ns()

@app.after_request
def after_request_func(response: Response) -> Response:
    request_end = time.time_ns()
    duration = (request_end - request.environ["request_start"]) / 1_000_000_000 # convert ns to s
    request_instruments["error_rate"].add(1, {
            "http.route": request.path,
            "state": "success" if response.status_code < 400 else "fail",
        }
    )
    request_instruments["http.server.request.duration"].record(
        duration,
        attributes = {
            "http.request.method": request.method,
            "http.route": request.path,
            "http.response.status_code": response.status_code
        }
    )
    return response

@app.route("/users", methods=["GET"])
def get_user():
    user, status = db.get_user(123)
    data = {}
    if user is not None:
        data = {"id": user.id, "name": user.name, "address": user.address}
    response = make_response(data, status)
    return response


def do_stuff():
    time.sleep(0.1)
    url = "http://httpbin:80/anything"
    response = requests.get(url)

@app.route("/")
def index():
    request_instruments["traffic_volume"].add(
        1, attributes={"http.route": request.path}
    )
    do_stuff()
    current_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
    return f"Hello, World! It's currently {current_time}"


if __name__ == "__main__":
    logging.getLogger("werkzeug").disabled = True
    request_instruments = create_request_instruments(meter)
    db = ChaosClient(client=FakerClient())
    app.run(host="0.0.0.0", debug=True)
