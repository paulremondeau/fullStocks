#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from src.utils import (
    request_stock_time_series,
    format_sending_data,
    evaluate_stats_information,
)
from config import API_KEY, FRONTEND_URL

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
    },
)
logger.info("Backend server initialized.")
# =================================================================================================
#     Database
# =================================================================================================

db = SQLAlchemy(app)
ma = Marshmallow(app)


class StockTimeSeries(db.Model):
    symbol = db.Column(db.String(10), primary_key=True)
    dateValue = db.Column(db.PickleType())
    stockValues = db.Column(db.PickleType())

    def __init__(self, symbol, date_value, time_series):
        self.symbol = symbol
        self.dateValue = date_value
        self.stockValues = time_series


class StockTimeSeriesSchema(ma.Schema):
    class Meta:
        fields = ("symbol", "dateValue", "stockValues")


class MarketState(db.Model):
    name = db.Column(db.String(10), primary_key=True)
    country = db.Column(db.String(30))
    is_market_open = db.Column(db.Boolean)
    time_to_open = db.Column(db.DateTime)
    date_check = db.Column(db.DateTime)

    def __init__(self, name, country, is_market_open, time_to_open, date_check):
        self.name = name
        self.country = country
        self.is_market_open = is_market_open
        self.time_to_open = time_to_open
        self.date_check = date_check


class MarketStateSchema(ma.Schema):
    class Meta:
        fields = ("name", "country", "isMarketOpen", "timeToOpen", "dateCheck")


# stock_time_series_schema = StockTimeSeriesSchema(many=True)
db.create_all()

logger.info("Database initialized.")

# =================================================================================================
#     Routes
# =================================================================================================


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
    logger.info(f"Starting function check_data_symbol({symbol})...")
    data_symbol = db.session.get(StockTimeSeries, symbol)
    # data_symbol = StockTimeSeries.query.get(symbol)
    if data_symbol is None:
        response = {"dataExists": False}
        logger.info(f"No data found for symbol {symbol}.")
    else:
        response = {"dataExists": True}
        logger.info(f"Data found for symbol {symbol}.")
        time_delta = datetime.datetime.today() - data_symbol.dateValue[-1]

        data_is_fresh = time_delta <= datetime.timedelta(days=1)
        response["dataIsFresh"] = data_is_fresh
        logger.info(f"Data is fresh : {data_is_fresh}.")

    logger.info(f"Function check_data_symbol({symbol}) completed !")
    return response


@app.route("/check_market_state/<symbol>", methods=["PUT"])
def check_market_state(symbol: str) -> Dict[str, str]:
    """Check the states of the market

    This function verifies if the markets are open.
    Update information in the database.

    Returns
    -------
    ...
        ...
    """

    return


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
            logger.warning(
                f"No data in database for symbol {symbol} with method {method}."
            )
            logger.warning(f"Request is KO. Returning None.")
            status = "ko"
            stocks_date = None
            stock_values = None
            json_stats = None

        else:
            logger.info(f"Data in database for symbol {symbol} with method {method}.")
            logger.info(f"Request is OK. Retrieving data for symbol {symbol}...")
            stocks_date = stock_time_series_symbol_data.dateValue
            stock_values = stock_time_series_symbol_data.stockValues
            time_series_df = pd.Series(stock_values, index=stocks_date)
            json_stats = evaluate_stats_information(time_series_df, symbol)
            logger.info(f"Data for symbol {symbol} retrieved from database !")

    if method in ["POST", "PUT"]:
        logger.info(
            f"Fetching data for symbol {symbol} with method {method} from Twelve data API..."
        )
        twelve_data_status, time_series = request_stock_time_series(symbol, API_KEY)

        if twelve_data_status == "error":
            logger.warning(
                f"Fetching data for symbol {symbol} with method {method} from Twelve data API failed."
            )
            logger.warning(f"Request is KO. Returning None.")
            status = "ko"
            stocks_date = None
            stock_values = None
            json_stats = None

        else:
            logger.info(
                f"Fetching data for symbol {symbol} with method {method} from Twelve data API succeded !"
            )
            json_stats = evaluate_stats_information(time_series, symbol)
            stocks_date = list(time_series.index)
            stock_values = list(time_series.values)

            # POST method
            if method == "POST":
                logger.info(f"Adding data for symbol {symbol} in database... ")
                new_timeseries = StockTimeSeries(symbol, stocks_date, stock_values)
                db.session.add(new_timeseries)

                db.session.commit()
                logger.info(f"Data for symbol {symbol} added to database !")

            # PUT method
            elif method == "PUT":
                logger.info(f"Fetching data for symbol {symbol} in database... ")
                old_timeseries = db.session.get(StockTimeSeries, symbol)
                if (
                    old_timeseries is None
                ):  # TODO : unnecessary, should be removed after further testing...
                    logger.warning(
                        f"No data in database for symbol {symbol} with method {method}."
                    )
                    logger.warning(f"Request is KO. Returning None.")
                    status = "ko"
                    stocks_date = None
                    stock_values = None
                    json_stats = None

                else:
                    logger.info(f"Data for symbol {symbol} in database retrieved !")
                    old_timeseries.dateValue = stocks_date
                    old_timeseries.stockValues = stock_values

                    db.session.commit()
                    logger.info(f"Data for symbol {symbol} in database updated !")

    logger.info(f"Formating data for the frontend...")
    response_formatted_data = format_sending_data(stocks_date, stock_values)
    logger.info(f"Data succesfuly formated for the frontend !")

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
    from waitress import serve

    serve(app, host="0.0.0.0", port=5000)
