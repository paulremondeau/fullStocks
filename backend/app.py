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

convert_delta_unit = {
    "min": "minutes",
    "h": "hours",
    "day": "days",
    "month": "months",
    "week": "weeks",
}

DELTA_CHOICES = [
    "1min",
    "5min",
    "15min",
    "30min",
    "45min",
    "1h",
    "2h",
    "4h",
    "1day",
    "1week",
    "1month",
]

# =================================================================================================
#     Libs
# =================================================================================================

import json
import re
import os
import datetime
from typing import Dict, List
import logging
import logging.config

import pandas as pd
import pytz

EUROPE_TIMEZONE = pytz.timezone("Europe/Paris")

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint

from src import request_twelvedata_api, stock_stats, utils

from config import API_KEY, API_PLAN, FRONTEND_URL

basedir = os.path.abspath(os.path.dirname(__file__))

# =================================================================================================
#     LOGS
# =================================================================================================


logging.config.fileConfig(os.path.join(basedir, LOG_CONFIG_FILE))
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
        r"/symbols/*": {"origins": FRONTEND_URL},
        r"/market": {"origins": FRONTEND_URL},
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
    timeDelta = db.Column(db.String(6), primary_key=True)
    exchange = db.Column(db.String(EXCHANGE_LENGTH))
    timezone = db.Column(db.String(100))
    timeseries = db.Column(db.PickleType(comparator=pd.Series.equals))
    marketChecked = db.Column(db.Boolean)

    def __init__(
        self, symbol, timeDelta, exchange, timezone, timeseries, marketChecked
    ):
        self.symbol = symbol
        self.timeDelta = timeDelta
        self.exchange = exchange
        self.timezone = timezone
        self.timeseries = timeseries
        self.marketChecked = marketChecked


class StockTimeSeriesSchema(ma.Schema):
    class Meta:
        fields = (
            "symbol",
            "timeDelta",
            "exchange",
            "timezone",
            "timeseries",
            "marketChecked",
        )


stock_timeseries_schema = StockTimeSeriesSchema()
stocks_timeseries_schema = StockTimeSeriesSchema(many=True)


class MarketState(db.Model):
    exchange = db.Column(db.String(EXCHANGE_LENGTH), primary_key=True)
    country = db.Column(db.String(COUNTRY_LENGTH))
    isMarketOpen = db.Column(db.Boolean)
    timeToOpen = db.Column(db.PickleType())
    timeToClose = db.Column(db.PickleType())
    dateCheck = db.Column(db.Float)

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


market_schema = MarketStateSchema()
markets_schema = MarketStateSchema(many=True)


class AvailableSymbols(db.Model):
    exchange = db.Column(db.String(EXCHANGE_LENGTH), primary_key=True)
    symbolsList = db.Column(db.PickleType())
    dateCheck = db.Column(db.Float)

    def __init__(self, exchange, symbolsList, dateCheck):
        self.exchange = exchange
        self.symbolsList = symbolsList
        self.dateCheck = dateCheck


class AvailableSymbolsSchema(ma.Schema):
    class Meta:
        fields = (
            "exchange",
            "symbolsList",
            "dateCheck",
        )


available_symbols_schema = AvailableSymbolsSchema()
available_symbols_many_schema = AvailableSymbolsSchema(many=True)

db.create_all()

logger.info("Database initialized.")

# =================================================================================================
#     Routes
# =================================================================================================


@app.route("/symbols", methods=["GET"])
def get_all_symbols_data():
    """Get all symbols at once.

    Get the list of all the symbols data available in database.
    ---
    tags:
        - SYMBOLS
    responses:
        200:
            description: Request successful, returning all symbols data from database and the evaluated stats infomartions.
            schema:
                type: object
                properties:
                    timeseries:
                        type: array
                        description: The symbols timeseries.
                        items:
                            type: array
                            description: One symbol timeseries.
                            items:
                                type: array
                                items:
                                    type: number
                                    description: A data point (time and value).
                                minItems: 2
                                maxItems: 2

                    stats:
                        type: array
                        description: The list of the stats informations of the stocks.
                        items:
                            type: object
                            properties:
                                symbol:
                                    type: string
                                    description: The symbol name.
                                cumulativeReturn:
                                    type: number
                                    description: The cumulative return of the stock.
                                annualizedCumulativeReturn:
                                    type: number
                                    description: The annualized cumulative return of the stock.
                                annualizedVolatility:
                                    type: number
                                    description: The annualized volatility of the stock.




    """
    target_data_format: str = request.args.get(
        "dataFormat", default="apexcharts", type=str
    )
    localize: bool = request.args.get("localize", default=False, type=json.loads)
    performance: bool = request.args.get("performance", default=True, type=json.loads)

    data = StockTimeSeries.query.all()

    all_timeseries: Dict[
        str, str | List[List[float | int]]
    ] = stocks_timeseries_schema.dump(data)

    stats_table = [
        stock_stats.evaluate_stats_information(entry["timeseries"], entry["symbol"])
        for entry in all_timeseries
    ]

    for entry in all_timeseries:
        entry["timeseries"] = utils.series_to_apexcharts(
            entry["timeseries"], performance
        )

    return {"timeseries": all_timeseries, "stats": stats_table}, 200


@app.route("/symbols", methods=["POST"])
def create_symbol_data():
    """Add a new symbol.

    Add a symbol timeseries to the database.
    ---
    tags:
        - SYMBOLS

    parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
                symbol:
                    type: string
                    description: The symbol we want to add to the database.
                timeDelta:
                    type: string
                    description: The desired time delta for the data.

    responses:
        200:
            description: Data already exists in the database, you can use directly the get method.
        201:
            description: Data successfully created in the database, you can use the get method to retrieve it.
        500:
            description: An error happened sever-side.
            schema:
                type: object
                properties:
                    status:
                        type: string
                        description: The status of the request, which will be 'error' in this case
                    code:
                        type: integer
                        description: The associated error code.
                    message:
                        type: string
                        description: The error message associated.
    """
    requests_body = json.loads(request.data)
    try:
        symbol = requests_body["symbol"]
        time_delta = requests_body["timeDelta"]
    except KeyError:
        return {
            "message": "Body format wrong, should be {'symbol': 'abc', 'timeDelta': 'abc}"
        }, 400

    if db.session.get(StockTimeSeries, [symbol, time_delta]) is not None:
        # Data already exist
        return {
            "message": f"Data already exists, use GET /symbols/{symbol}?timeDelta={time_delta}"
        }, 200

        # return {"message": f"Data already exists, use /symbols/{symbol}"}, 409

    else:
        # Data does not exists
        result_from_twelve_data = request_twelvedata_api.get_stock_timeseries(
            symbol, time_delta, API_KEY
        )

        if result_from_twelve_data["status"] == "ok":
            exchange = result_from_twelve_data["exchange"]
            market_check = False
            market_data = db.session.get(MarketState, exchange)

            if market_data is not None:
                if market_data.isMarketOpen:
                    market_check = True

            new_timeseries = StockTimeSeries(
                symbol,
                time_delta,
                exchange=result_from_twelve_data["exchange"],
                timezone=result_from_twelve_data["timezone"],
                timeseries=result_from_twelve_data["data"],
                marketChecked=False,
            )

            db.session.add(new_timeseries)
            db.session.commit()

            return {
                "message": f"Data created, use GET /symbols/{symbol}?timeDelta={time_delta}"
            }, 201
        else:
            return result_from_twelve_data, 500


@app.route("/symbols/<symbol>", methods=["GET"])
def get_symbol_data(symbol: str):
    """Retrieve one specific symbol.

    Get timeseries and statistics informations of the given stock symbol.
    ---
    tags:
        - SYMBOLS
    parameters:
        - in: path
          name: symbol
          schema:
            type: string
          required: true
          description: The symbol we want to retrieve data from the database.
        - in: query
          name: timeDelta
          schema:
              type: string
          required: true
          description: The time interval we want for the data.
        - in: query
          name: performance
          schema:
              type: boolean
          required: true
          description: To format to performance or keep raw value.
    responses:
        200:
            description: Request successful, returning the symbol data from database and the evaluated stats infomartions.
            schema:
                type: object
                properties:
                    timeseries:
                        type: array
                        description: Timeseries, either performance or raw value.
                        items:
                            type: array
                            items:
                                type: number
                                description: A data point (time and value).
                            minItems: 2
                            maxItems: 2
                    stats:
                        type: object
                        description: The stats informations of the stock.
                        properties:
                            symbol:
                                type: string
                                description: The symbol name.
                            cumulativeReturn:
                                type: number
                                description: The cumulative return of the stock.
                            annualizedCumulativeReturn:
                                type: number
                                description: The annualized cumulative return of the stock.
                            annualizedVolatility:
                                type: number
                                description: The annualized volatility of the stock.

        204:
            description: Data does not exist in database, you can create it through the POST /symbols
    """
    time_delta: str = request.args.get("timeDelta", type=str)
    performance: bool = json.loads(request.args.get("performance"))

    data = db.session.get(StockTimeSeries, [symbol, time_delta])
    if data is None:
        # Data does not exist
        return {}, 204

    else:
        database_data = stock_timeseries_schema.dump(data)

        stats_table = stock_stats.evaluate_stats_information(
            database_data["timeseries"], symbol
        )

        timeseries = utils.series_to_apexcharts(
            database_data["timeseries"], performance=performance
        )

        return {"timeseries": timeseries, "stats": stats_table}, 200


# TODO : market is closed but new data is available (delta > 2* chosen delta) -> modify this !!
@app.route("/symbols/<symbol>", methods=["PUT"])
def update_symbol_data(symbol: str):
    """Update one specific symbol.

    Update data symbol in the database.
    ---
    tags:
        - SYMBOLS
    parameters:
        - in: path
          name: symbol
          schema:
            type: string
          required: true
          description: The symbol we want to update data in the database.
        - in: query
          name: timeDelta
          schema:
              type: string
          required: true
          description: The time interval we want for the data.
    responses:
        200:
            description: The data was successfully updated, you can get it back with get request.
        204:
            description: The data does not exists, you should create it first with POST /symbols.

        304:
            description: The data was not updated because it was fresh enough or the associated market was closed.

        400:
            description: Time delta is incorrect, choose according to message.
            schema:
                type: object
                properties:
                    message:
                        type: string
                        description: Gives the list of available time delta.
        500:
            description: An error happened server-side.
            schema:
                type: object
                properties:
                    status:
                        type: string
                        description: The status of the request, which will be 'error' in this case.
                    code:
                        type: integer
                        description: The associated error code.
                    message:
                        type: string
                        description: The error message associated.
    """
    time_delta: str = request.args.get("timeDelta", type=str)
    if time_delta not in DELTA_CHOICES:
        return {
            "message": f'Incorrect time delta, should be within {", ".join(DELTA_CHOICES)}'
        }, 400

    old_data = db.session.get(StockTimeSeries, [symbol, time_delta])
    if old_data is None:
        # Data does not exist
        return {}, 204

    else:
        # Check if data is fresh enough
        timezone = old_data.timezone
        tz = pytz.timezone(timezone)
        delta_size = int(re.findall("\d+", time_delta)[0])
        delta_unit = convert_delta_unit[re.findall("\D+", time_delta)[0]]

        if delta_unit == "months":
            delta_unit = "days"
            delta_size *= 30

        data_time_delta = datetime.datetime.now(tz=tz) - tz.localize(
            old_data.timeseries.index[-1]
        )

        if data_time_delta < datetime.timedelta(**{delta_unit: delta_size}):
            # if True:
            # Data is fresh enough
            logger.warning(
                f"Last data point is younger than {delta_size} {delta_unit}, no new data available. Last data is {data_time_delta} old."
            )
            return {}, 304

        else:
            # Data is not fresh enough, now check if market is open
            exchange_data = db.session.get(MarketState, old_data.exchange)

            if not exchange_data:
                return {"message": f"No market data for {old_data.exchange}"}, 409

            if not exchange_data.isMarketOpen:
                # Market is close

                if not old_data.marketChecked:
                    logger.info(
                        f"{old_data.exchange} is closed, we verify one time for potential new data."
                    )
                    # Check at least one time because new data may have arrived
                    old_data.marketChecked = True

                else:
                    logger.warning(
                        f"{old_data.exchange} is closed and verified, no new data available."
                    )
                    return {}, 304

            else:
                old_data.marketChecked = False

            result_from_twelve_data = request_twelvedata_api.get_stock_timeseries(
                symbol, time_delta, API_KEY
            )
            if result_from_twelve_data["status"] == "ok":
                old_data.timeseries = result_from_twelve_data["data"]

                db.session.commit()

                return {
                    "message": f"Data successfully updated, use GET /symbols/{symbol}?timeDelta={time_delta}"
                }, 200

            else:
                return result_from_twelve_data, 500


@app.route("/market", methods=["GET"])
def get_market_state():
    """Get the market informations.

    Get the market state data.
    ---
    tags:
        - MARKET
    responses:
        200:
            description: Request successful, returning market data
            schema:
                type: array
                items:
                    type: object
                    properties:
                        exchange:
                            type: string
                            description: The market exchange name.

                        country:
                            type: string
                            description: The country of the market.

                        isMarketOpen:
                            type: boolean
                            description: Indicates if the market is open.

                        timeToOpen:
                            type: integer
                            description: If the market is close, indicates the time before opening (timestamp duration).

                        timeToClose:
                            type: integer
                            description: If the market is open, indicates the time before close (timestamp duration).

                        dateCheck:
                            type: number
                            description: Indicates the timestamp when the market check was made.

        204:
            description: The data does not exist in database, you can create it with POST /market.


    """
    data = MarketState.query.all()

    if not data:
        # Data does not exist
        return {}, 204

    market: Dict[str, str | List[List[float | int]]] = markets_schema.dump(data)
    market = pd.DataFrame(market)

    market = [json.loads(x.to_json()) for x in market.iloc]

    return market, 200


@app.route("/market", methods=["POST"])
def create_market_state():
    """Create the market informations.

    Create the market state in database.
    ---
    tags:
        - MARKET
    responses:
        200:
            description: The data already exists, you can get it with GET /market.
        201:
            description: The data was successfully created, you can get it with GET /market.
        500:
            description: An error happened server-side.
            schema:
                type: object
                properties:
                    status:
                        type: string
                        description: The status of the request, which will be 'error' in this case
                    code:
                        type: integer
                        description: The associated error code.
                    message:
                        type: string
                        description: The error message associated.

    """
    data = MarketState.query.all()

    if data:
        # Data already exists

        return {"message": f"Data already exists, use GET /market"}, 200

    else:
        result_from_twelve_data = request_twelvedata_api.get_markets_state(API_KEY)
        if result_from_twelve_data["status"] == "ok":
            date_check = datetime.datetime.now(tz=EUROPE_TIMEZONE).timestamp()
            data_market = result_from_twelve_data["data"]
            data_market = data_market.drop_duplicates(subset=["exchange"])
            for data_exchange in data_market.iloc:
                # Adding each market one by one
                logger.info(data_market["exchange"].value_counts())
                db.session.add(
                    MarketState(
                        exchange=data_exchange["exchange"],
                        country=data_exchange["country"],
                        isMarketOpen=data_exchange["isMarketOpen"],
                        timeToOpen=data_exchange["timeToOpen"],
                        timeToClose=data_exchange["timeToClose"],
                        dateCheck=date_check,
                    )
                )

            db.session.commit()

        else:
            # Error
            return result_from_twelve_data, 500

    return {"message": f"Data succesfully created, use GET /market"}, 201


@app.route("/market", methods=["PUT"])
def update_market_state():
    """Update the market informations.

    Update the market data.
    ---
    tags:
        - MARKET
    responses:
        200:
            description: The data was successfully updated, you can get it with GET /market.

        204:
            description: The data does not exist in database, you can create it with POST /market.

        500:
            description: An error happened server-side.
            schema:
                type: object
                properties:
                    status:
                        type: string
                        description: The status of the request, which will be 'error' in this case.
                    code:
                        type: integer
                        description: The associated error code.
                    message:
                        type: string
                        description: The error message associated.
    """
    data = MarketState.query.all()
    if not data:
        # Data does not exist
        return {}, 204

    else:
        result_from_twelve_data = request_twelvedata_api.get_markets_state(API_KEY)
        if result_from_twelve_data["status"] == "ok":
            data_market = result_from_twelve_data["data"]

            date_check = datetime.datetime.now(tz=EUROPE_TIMEZONE).timestamp()

            for data_exchange in data_market.iloc:
                old_exchange_data = db.session.get(
                    MarketState, data_exchange["exchange"]
                )
                if old_exchange_data is None:
                    # TODO : adding new data to database through PUT request... Ugly...
                    # No data for this exchange, lets add it to the database
                    db.session.add(
                        MarketState(
                            exchange=data_exchange["exchange"],
                            country=data_exchange["country"],
                            isMarketOpen=data_exchange["isMarketOpen"],
                            timeToOpen=data_exchange["timeToOpen"],
                            timeToClose=data_exchange["timeToClose"],
                            dateCheck=date_check,
                        )
                    )

                else:
                    old_exchange_data.isMarketOpen = data_exchange["isMarketOpen"]
                    old_exchange_data.timeToOpen = data_exchange["timeToOpen"]
                    old_exchange_data.timeToClose = data_exchange["timeToClose"]
                    old_exchange_data.dateCheck = date_check

            db.session.commit()

        else:
            # Error
            return result_from_twelve_data, 500

    return {"message": f"Data successfully updated, use GET /market"}, 200


@app.route("/symbols-list", methods=["GET"])
def get_symbols_list():
    """Get the available symbols.

    Get the symbols available for the given plan.
    ---
    tags:
        - SYMBOLS, SYMBOLS LIST
    responses:
        200:
            description: Request successful, returning available symbols.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        exchange:
                            type: string
                            description: The market exchange name.
                        symbolsList:
                            type: array
                            description: The available symbols list for this exchange.
                            items:
                                type: string
                                description: Symbol available.
                        dateCheck:
                            type: number
                            description: The date of the last check.

        204:
            description: The data does not exist in database, you can create it with POST /symbols-list.

        500:
            description: An error happened server-side.
            schema:
                type: object
                properties:
                    status:
                        type: string
                        description: The status of the request, which will be 'error' in this case.
                    code:
                        type: integer
                        description: The associated error code.
                    message:
                        type: string
                        description: The error message associated.
    """
    data = AvailableSymbols.query.all()

    if not data:
        return {}, 204

    symbols_list: Dict[str, str | List[str]] = available_symbols_many_schema.dump(data)

    return symbols_list, 200


@app.route("/symbols-list", methods=["POST"])
def create_symbols_list():
    """Create the available symbols list.

    Create the symbols available for the given plan.
    ---
    tags:
        - SYMBOLS, SYMBOLS LIST
    responses:

        200:
            description: The data exists already in database, you can update it with PUT /symbols-list.

        201:
            description: The data was successfully created, you can get it with GET /symbols-list.

        500:
            description: An error happened server-side.
            schema:
                type: object
                properties:
                    status:
                        type: string
                        description: The status of the request, which will be 'error' in this case.
                    code:
                        type: integer
                        description: The associated error code.
                    message:
                        type: string
                        description: The error message associated.
    """
    data = AvailableSymbols.query.all()
    if data:
        # Data exists already
        return {"message": f"Data already exists, use GET /market"}, 200

    else:
        result_from_twelve_data = request_twelvedata_api.get_available_symbols_list(
            API_KEY, API_PLAN
        )

        if result_from_twelve_data["status"] == "ok":
            date_check = datetime.datetime.now(tz=EUROPE_TIMEZONE).timestamp()

            for exchange, symbols_list in result_from_twelve_data["data"].items():
                db.session.add(
                    AvailableSymbols(
                        exchange=exchange,
                        symbolsList=symbols_list,
                        dateCheck=date_check,
                    )
                )

            db.session.commit()

        else:
            # Error
            return result_from_twelve_data, 500

    return {"message": f"Data successfully created, use GET /symbols-list"}, 201


@app.route("/symbols-list", methods=["PUT"])
def update_symbols_list():
    """Update the available symbols list.

    Update the symbols available for the given plan.
    ---
    tags:
        - SYMBOLS, SYMBOLS LIST
    responses:
        200:
            description: The data was successfully updated, you can get it with GET /symbols-list.

        204:
            description: The data does not exist in database, you can create it with POST /symbols-list.

        500:
            description: An error happened server-side.
            schema:
                type: object
                properties:
                    status:
                        type: string
                        description: The status of the request, which will be 'error' in this case.
                    code:
                        type: integer
                        description: The associated error code.
                    message:
                        type: string
                        description: The error message associated.
    """
    data = AvailableSymbols.query.all()

    if not data:
        return {}, 204

    data_dumped = available_symbols_many_schema.dump(data)
    date_check = data_dumped[0]["dateCheck"]

    time_delta = datetime.datetime.now(
        tz=EUROPE_TIMEZONE
    ) - datetime.datetime.fromtimestamp(date_check, tz=EUROPE_TIMEZONE)

    if time_delta < datetime.timedelta(days=1):
        # if True:
        # Data is fresh enough
        logger.warning(
            f"Last update of available symbols list is not older than 1, no new data available. Last data is {time_delta} old."
        )
        return {}, 304

    else:
        result_from_twelve_data = request_twelvedata_api.get_available_symbols_list(
            API_KEY, API_PLAN
        )

        if result_from_twelve_data["status"] == "ok":
            date_check = datetime.datetime.now(tz=EUROPE_TIMEZONE).timestamp()

            for exchange, symbols_list in result_from_twelve_data["data"].items():
                old_data = db.session.get(AvailableSymbols, exchange)
                if old_data is None:
                    # Crate data
                    db.session.add(
                        AvailableSymbols(
                            exchange=exchange,
                            symbolsList=symbols_list,
                            dateCheck=date_check,
                        )
                    )
                else:
                    # Update data
                    old_data.symbolsList = symbols_list
                    old_data.dateCheck = date_check

            db.session.commit()

        else:
            # Error
            return result_from_twelve_data, 500

    return {}, 200


@app.route("/spec")
def spec():
    swag = swagger(app)
    swag["info"]["version"] = "1.0"
    swag["info"]["title"] = "Full Stocks backend"

    return json.dumps(swag)


# Start the app
if __name__ == "__main__":
    # Production server

    SWAGGER_URL = "/api/docs"
    API_URL = "/spec"
    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)

    from waitress import serve

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    serve(app, host="0.0.0.0", port=5000)
