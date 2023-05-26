import json

from flask import Flask, jsonify
from flask_cors import CORS

from src.utils import request_stock_time_series, request_avalaible_symbols


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})


# sanity check route
@app.route("/symbol/<symbol>", methods=["GET"])
def request_data(symbol: str):
    time_series, statistics_informations = request_stock_time_series(symbol)
    times_series = [
        [int(index), float(f"{value:.2f}")] for index, value in time_series.items()
    ]
    return json.dumps({"timeSeries": times_series, "stats": statistics_informations})


@app.route("/fetch_symbol", methods=["GET"])
def fetch_available_symbols():
    symbols_list = request_avalaible_symbols()
    return json.dumps({"symbolsList": symbols_list})


@app.route("/ping", methods=["GET"])
def ping_pong():
    return jsonify("pong!")
