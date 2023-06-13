#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""app.py:  app

This is the main app application file.
"""


__author__ = "Paul RÉMONDEAU"
__copyright__ = "Paul RÉMONDEAU"
__version__ = "1.0.0"
__maintainer__ = "Paul RÉMONDEAU"
__email__ = "paulremondeau@yahoo.fr"
__status__ = "Production"
__logger__ = "app.py"

LOG_CONFIG_FILE = "config/log_config.ini"

# =================================================================================================
#     Libs
# =================================================================================================

import json
import os
import datetime
from typing import Dict, List
import logging
import logging.config

import pandas as pd

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

from src import request_twelvedata_api, stock_stats, utils

from config import API_KEY, API_PLAN, FRONTEND_URL

basedir = os.path.abspath(os.path.dirname(__file__))

# =================================================================================================
#     LOGS
# =================================================================================================


logging.config.fileConfig(LOG_CONFIG_FILE)
logger = logging.getLogger(__logger__)
logger.info("Logger initialized.")


# =================================================================================================
#     Flask App
# =================================================================================================

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
        r"/check_symbol_data/*": {"origins": FRONTEND_URL},
        r"/get_symbol_data/*": {"origins": FRONTEND_URL},
        r"/check_market_state/*": {"origins": FRONTEND_URL},
    },
)
logger.info("Backend server initialized.")

# =================================================================================================
#     Database
# =================================================================================================

db = SQLAlchemy(app)
ma = Marshmallow(app)

SYMBOL_LENGTH = 20
EXCHANGE_LENGTH = 30
COUNTRY_LENGTH = 30


class StockTimeSeries(db.Model):
    symbol = db.Column(db.String(SYMBOL_LENGTH), primary_key=True)
    exchange = db.Column(db.String(EXCHANGE_LENGTH))
    dateValue = db.Column(db.PickleType())
    stockValues = db.Column(db.PickleType())

    def __init__(self, symbol, exchange, date_value, time_series):
        self.symbol = symbol
        self.exchange = exchange
        self.dateValue = date_value
        self.stockValues = time_series


class StockTimeSeriesSchema(ma.Schema):
    class Meta:
        fields = ("symbol", "exchange", "dateValue", "stockValues")


class MarketState(db.Model):
    exchange = db.Column(db.String(EXCHANGE_LENGTH), primary_key=True)
    country = db.Column(db.String(COUNTRY_LENGTH))
    isMarketOpen = db.Column(db.Boolean)
    timeToOpen = db.Column(db.PickleType())
    timeToClose = db.Column(db.PickleType())
    dateCheck = db.Column(db.DateTime)

    def __init__(
        self, exchange, country, isMarketOpen, timeToOpen, timeToClose, dateCheck
    ):
        self.exchange = exchange
        self.country = country
        self.isMarketOpen = isMarketOpen
        self.timeToOpen = timeToOpen
        self.timeToClose = timeToClose
        self.dateCheck = dateCheck


class MarketStateSchema(ma.Schema):
    class Meta:
        fields = (
            "exchange",
            "country",
            "isMarketOpen",
            "timeToOpen",
            "timeToClose",
            "dateCheck",
        )


db.create_all()

logger.info("Database initialized.")

# =================================================================================================
#     Routes
# =================================================================================================


@app.route("/check_symbol_data/<symbol>", methods=["GET"])
def check_symbol_data(symbol: str) -> Dict[str, str]:
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
    logger.info(f"Starting function check_symbol_data({symbol})...")
    data_symbol = db.session.get(StockTimeSeries, symbol)
    # data_symbol = StockTimeSeries.query.get(symbol)
    if data_symbol is None:
        response = {"dataExists": False}

    else:
        response = {"dataExists": True}

        time_delta = datetime.datetime.today() - data_symbol.dateValue[-1]
        data_is_fresh = time_delta <= datetime.timedelta(days=1)
        response["dataIsFresh"] = data_is_fresh

        if not data_is_fresh:
            exchange = data_symbol.exchange
            exchange_data = db.session.get(MarketState, exchange)
            market_open = exchange_data.isMarketOpen
            response["isMarketOpen"] = market_open

    logger.info(f"Function check_symbol_data({symbol}) completed ! Result : {response}")
    return response


@app.route("/check_market_state", methods=["GET"])
def check_market_state() -> Dict[str, str]:
    """Check the states of the market

    This function verifies if the markets are open.
    Update information in the database.

    Returns
    -------
    ...
        ...
    """

    logger.info(f"Starting function check_market_state()...")
    status = "ok"

    result_from_twelve_data = request_twelvedata_api.get_markets_state(API_KEY)
    twelve_data_status = result_from_twelve_data["status"]

    if twelve_data_status == "error":
        status = "ko"
        result_data = None

    else:
        data_market = result_from_twelve_data["data"]
        data_market["dateCheck"] = datetime.datetime.now()
        for data_exchange in data_market.iloc:
            exchange = data_exchange["exchange"]

            country = data_exchange["country"]
            isMarketOpen = data_exchange["isMarketOpen"]
            timeToOpen = data_exchange["timeToOpen"]
            timeToClose = data_exchange["timeToClose"]
            dateCheck = data_exchange["dateCheck"]

            old_exchange_data = db.session.get(MarketState, exchange)
            if old_exchange_data is None:
                new_exchange_data = MarketState(
                    exchange,
                    country,
                    isMarketOpen,
                    timeToOpen,
                    timeToClose,
                    dateCheck,
                )
                db.session.add(new_exchange_data)
                db.session.commit()

            else:
                old_exchange_data.country = country
                old_exchange_data.isMarketOpen = isMarketOpen
                old_exchange_data.timeToOpen = timeToOpen
                old_exchange_data.timeToClose = timeToClose
                old_exchange_data.dateCheck = dateCheck

                db.session.commit()

        result_data = [json.loads(x.to_json()) for x in data_market.iloc]

    logger.info(f"Function check_market_state() finished !")
    return json.dumps({"status": status, "data": result_data})


@app.route("/get_symbol_data/<symbol>", methods=["POST", "GET", "PUT"])
def request_data(symbol: str) -> Dict[str, str | dict | List[list]]:
    """Retrieves symbol data.

    This function retrieves data for the given symbol.
    The function works different with the method request:
    - GET : data is stored in the database. Data is then retrieved
    from the database.
    - POST : data does not exists in database. Data is fetched
    from the Twelve Data API and stored in database.
    - PUT data is stored in database but we want to fetch
    from the Twelve DATA API nonetheless and update
    the data in the database.


    Parameters
    ----------
    symbol : str
        The stock symbol of which we want the data.

    Returns
    -------
    Dict[str, str | dict | List[list]]
        Data for frontend.
    """
    method = request.method
    logger.info(f"Starting function request_data({symbol})...")
    logger.info(f"Method: {method}")
    status = "ok"

    # GET method
    if method == "GET":
        stock_time_series_symbol_data = db.session.get(StockTimeSeries, symbol)
        if stock_time_series_symbol_data is None:
            status = "ko"
            stocks_date = None
            stock_values = None
            json_stats = None

        else:
            stocks_date = stock_time_series_symbol_data.dateValue
            stock_values = stock_time_series_symbol_data.stockValues
            time_series_df = pd.Series(stock_values, index=stocks_date)
            json_stats = stock_stats.evaluate_stats_information(time_series_df, symbol)
            logger.info(f"Data for symbol {symbol} retrieved from database !")

    if method in ["POST", "PUT"]:
        result_from_twelve_data = request_twelvedata_api.request_stock_time_series(
            symbol, API_KEY
        )
        twelve_data_status = result_from_twelve_data["status"]

        if twelve_data_status == "error":
            status = "ko"
            stocks_date = None
            stock_values = None
            json_stats = None

        else:
            exchange = result_from_twelve_data["exchange"]
            time_series = result_from_twelve_data["data"]

            json_stats = stock_stats.evaluate_stats_information(time_series, symbol)
            stocks_date = list(time_series.index)
            stock_values = list(time_series.values)

            # POST method
            if method == "POST":
                new_timeseries = StockTimeSeries(
                    symbol, exchange, stocks_date, stock_values
                )
                db.session.add(new_timeseries)

                db.session.commit()

            # PUT method
            elif method == "PUT":
                old_timeseries = db.session.get(StockTimeSeries, symbol)
                if (
                    old_timeseries is None
                ):  # TODO : unnecessary, should be removed after further testing...
                    status = "ko"
                    stocks_date = None
                    stock_values = None
                    json_stats = None

                else:
                    old_timeseries.exchange = exchange
                    old_timeseries.dateValue = stocks_date
                    old_timeseries.stockValues = stock_values

                    db.session.commit()

    response_formatted_data: List[List[int | float]] = utils.format_sending_data(
        stocks_date, stock_values
    )

    logger.info(f"Function request_data({symbol}) completed !")
    return json.dumps(
        {
            "symbol": symbol,
            "data": response_formatted_data,
            "stats": json_stats,
            "status": status,
        }
    )


# Start the app
if __name__ == "__main__":
    # Production server

    from waitress import serve

    serve(app, host="0.0.0.0", port=5000)
