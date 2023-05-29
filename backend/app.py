import json
import os

from flask import Flask, jsonify
from flask_cors import CORS

from src.utils import request_stock_time_series, request_avalaible_symbols


# Set up the app and point it to Vue
app = Flask(__name__)
app.config.from_object(__name__)


# enable CORS
CORS(
    app,
    resources={r"/symbol/*": {"origins": "*"}, r"/fetch_symbol/*": {"origins": "*"}},
)


# Set up the index route
@app.route("/")
def index():
    return app.send_static_file("index.html")


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


# Start the app
if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=5000)
