import json
import os
import datetime
from typing import Dict

import pandas as pd

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

from src.utils import (
    request_stock_time_series,
    request_avalaible_symbols,
    format_sending_data,
    evaluate_stats_information,
)
from config import API_KEY

basedir = os.path.abspath(os.path.dirname(__file__))

# Set up the app and point it to Vue
app = Flask(__name__)
app.config.from_object(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "db.sqlite"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.app_context().push()

# enable CORS
cors = CORS(
    app,
    resources={
        r"/check_symbol_data/*": {"origins": "*"},
        r"/get_symbol_data/*": {"origins": "*"},
    },
)

db = SQLAlchemy(app)
ma = Marshmallow(app)


# Database
class StockTimeSeries(db.Model):
    symbol = db.Column(db.String(30), primary_key=True)
    dateValue = db.Column(db.PickleType())
    stockValues = db.Column(db.PickleType())

    def __init__(self, symbol, date_value, time_series):
        # Add the data to the instance
        self.symbol = symbol
        self.dateValue = date_value
        self.stockValues = time_series


class StockTimeSeriesSchema(ma.Schema):
    class Meta:
        fields = ("symbol", "dateValue", "stockValues")


stock_time_series_schema = StockTimeSeriesSchema(many=True)
# stock_stats_schema = StockStatsSchema(many=True)


@app.route("/check_symbol_data/<symbol>", methods=["GET"])
def check_data_symbol(symbol: str) -> Dict[str, str]:
    """Check if data exists and is up-to-date in databse.

    This function verifies if the data corresponding to the
    stocks requested exists in database, and if the data is not
    older than one day.

    Parameters
    ----------
    symbol : str
        The stock symbol we seeks information

    Returns
    -------
    Dict[str, str]
        The dict with response information
    """
    data_symbol = StockTimeSeries.query.get(symbol)
    if data_symbol is None:
        response = {"dataExists": False}
    else:
        response = {"dataExists": True}
        time_delta = datetime.datetime.today() - data_symbol.dateValue[-1]

        response["dataIsFresh"] = time_delta <= datetime.timedelta(days=1)

    return response


@app.route("/get_symbol_data/<symbol>", methods=["POST", "GET", "PUT"])
def request_data(symbol: str):
    method = request.method
    status = "ok"

    # GET method
    if method == "GET":
        stock_time_series_symbol_data = StockTimeSeries.query.get(symbol)
        if stock_time_series_symbol_data is None:
            status = "ko"
            stocks_date = None
            stock_values = None
            json_stats = None

        else:
            stocks_date = stock_time_series_symbol_data.dateValue
            stock_values = stock_time_series_symbol_data.stockValues
            time_series_df = pd.Series(stock_values, index=stocks_date)
            json_stats = evaluate_stats_information(time_series_df, symbol)

    if method in ["POST", "PUT"]:
        twelve_data_status, time_series = request_stock_time_series(symbol, API_KEY)

        if twelve_data_status == "error":
            status = "ko"
            stocks_date = None
            stock_values = None
            json_stats = None

        else:
            json_stats = evaluate_stats_information(time_series, symbol)
            stocks_date = list(time_series.index)
            stock_values = list(time_series.values)

            # POST method
            if method == "POST":
                new_timeseries = StockTimeSeries(symbol, stocks_date, stock_values)
                db.session.add(new_timeseries)

                # new_stats_table = StockStats(new_stats_table = StockStats(
                #     symbol,
                # )

                db.session.commit()

            # PUT method
            elif method == "PUT":
                old_timeseries = StockTimeSeries.query.get(symbol)
                if old_timeseries is None:
                    status = "ko"
                    stocks_date = None
                    stock_values = None
                    json_stats = None

                else:
                    old_timeseries.dateValue = stocks_date
                    old_timeseries.stockValues = stock_values

                    db.session.commit()

    response_formatted_data = format_sending_data(stocks_date, stock_values)

    return json.dumps(
        {
            "symbol": symbol,
            "data": response_formatted_data,
            "stats": json_stats,
            "status": status,
        }
    )


# @app.route("/symbol/<symbol>", methods=["GET"])
# def request_data(symbol: str):
#     time_series, statistics_informations = request_stock_time_series(symbol, API_KEY)
#     times_series = [
#         [int(index), float(f"{value:.2f}")] for index, value in time_series.items()
#     ]
#     return json.dumps({"stockValues": times_series, "stats": statistics_informations})


# @app.route("/fetch_symbol", methods=["GET"])
# def fetch_available_symbols():
#     symbols_list = request_avalaible_symbols(API_KEY)
#     return json.dumps({"symbolsList": symbols_list})


# Start the app
if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=5000)
