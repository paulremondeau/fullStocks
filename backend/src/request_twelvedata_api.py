#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""request_twelvedata_api.py:  function

This module is a gate between the Twelve Data API and this app.
"""

__author__ = "Paul RÉMONDEAU"
__copyright__ = "Paul RÉMONDEAU"
__version__ = "1.0.0"
__maintainer__ = "Paul RÉMONDEAU"
__email__ = "paulremondeau@yahoo.fr"
__status__ = "Production"
__logger__ = "request_twelvedata_api.py"

# =================================================================================================
#     Libs
# =================================================================================================

import os

from typing import List, Dict
from copy import copy

import requests
import pandas as pd
from typeguard import check_type


from .exceptions_twelvedata_api import TwelveDataApiException, handle_exception
from .utils import read_twelvedata_api_config_file

twelvedata_api_config_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "config",
    "twelvedata_api_info.json",
)

twelvedata_api_config = read_twelvedata_api_config_file(twelvedata_api_config_path)


# =================================================================================================
#     Functions
# =================================================================================================


def check_twelvedata_api_response(response: requests.Response) -> Dict[str, str | list]:
    """Format Twelve Data API response.

    This function take care of the data output from Twelve Data API.

    Parameters
    ----------
    response : requests.Response
        The Twelve Data API response.

    Returns
    -------
    Dict[str, str | list]
        This is the result format of the backend.

    Raises
    ------
    TwelveDataApiException
        Exception with the Twelve Data API
        code: the error code
        message: message related to the exception

    Examples
    ----------

    If the Twelve Data API returns good quality results for the ressource :

    >>> check_twelvedata_api_response(requests.get("http://api.twelvedata.com/ressource"))
    {"status": "ok", "data": ...}

    If the URL is ressources does not exists on the API :

    >>> check_twelvedata_api_response(requests.get("http://api.twelvedata.com/badRessource"))
    {"status": "error",  "code": 404, "message": "Not found"}

    If an error occured from Twelve Data API :

    >>> check_twelvedata_api_response(requests.get("http://api.twelvedata.com/badRessource"))
    {"status": "error",  "code": 429, "message": "You have run out of API credits for the current minute."}

    For a full list of errors, see https://twelvedata.com/docs#errors

    If the ressource is not what was expected :

    >>> check_twelvedata_api_response(requests.get("http://api.twelvedata.com/badRessource"))
    {"status": "error", "code": 500, "message": AssertionError or TypeCheckError message}

    """
    status_code_requests = response.status_code
    if status_code_requests == 404:
        # URL is not found
        raise TwelveDataApiException(404, "Not found")

    elif status_code_requests == 200:
        # Request succedeed
        response_json = response.json()
        if isinstance(response_json, list):
            # This is for the market data
            status = "ok"
            response_json = {"status": "ok", "data": response_json}

        else:
            status = response_json["status"]

        if status == "error":
            # An error occured with Twelve Data API
            code = response_json["code"]
            message = response_json["message"]

            raise TwelveDataApiException(code, message)

        else:
            return response_json

    else:
        # Statut code non géré
        raise TwelveDataApiException(501, "Not implemented")


@handle_exception
def get_stock_timeseries(
    symbol: str, api_key: str
) -> Dict[str, str | int | pd.DataFrame]:
    """Request the twelve data API for stock informations.

    This function requests meta and time series for the requested
    instrument. It also evaluates the cumulative return, the
    annualized cumulative return and  annualized volatility.

    Parameters
    ----------
    symbol : str
        The instrument symbol.

    Returns
    -------
    Dict[str, str | int | pd.DataFrame]
        res["status"] is ok or error
            - if status is error, dict contains code of error and message
            - if status is ok, dict contains exchange and data in dataframe

    Examples
    ----------

    Request time series for Apple :

    >>> res = get_stock_timeseries("AAPL", API_KEY)
    >>> res['status']
    ok
    >>> res['exchange']
    NASDAQ
    >>> res['timezone']
    America/New_York
    >>> res['data']
        datetime
    2019-06-20 04:00:00     49.69750
    2019-06-20 12:00:00     49.84485
    2019-06-21 04:00:00     50.06215
    2019-06-21 12:00:00     49.69250
    2019-06-24 04:00:00     49.87000
                            ...
    2023-06-06 09:30:00    179.16000
    2023-06-07 09:30:00    177.82001
    2023-06-08 09:30:00    180.53999
    2023-06-09 09:30:00    181.03999
    2023-06-12 09:30:00    183.84000
    Name: close, Length: 1228, dtype: float64

    If something went wrong :

    >>> get_stock_timeseries("AAPL", API_KEY)
    {"status": "error", "code": 500, "message": "Erreur"}

    See :func:`src.exceptions_twelvedata_api.handle_exception` for more informations on possible errors.
    """

    # API request
    params = copy(twelvedata_api_config["timeseries_params"])
    params["symbol"] = symbol
    params["apikey"] = api_key
    response = requests.get(twelvedata_api_config["timeseries_url"], params=params)

    response_json = check_twelvedata_api_response(response)

    meta: Dict[str, str] = check_type(response_json["meta"], Dict[str, str])

    values: List[Dict[str, str]] = check_type(
        response_json["values"], List[Dict[str, str]]
    )

    # Assert meta data is good format
    assert set(meta.keys()) == set(
        twelvedata_api_config["timeseries_meta_keys"]
    ), "Meta data are not correct, check Twelve Data API"

    exchange = meta["exchange"]
    timzezone = meta["exchange_timezone"]

    values = response_json["values"]
    # Check if values is not an empty list
    assert values, "Data value is empty, check Twelve Data API"

    values_keys = [x.keys() for x in response_json["values"]]

    # Assert that data is of type List[Dict] with all dict having same keys
    assert all(
        x == values_keys[0] for x in values_keys
    ), "Data value keys are not always the same, check Twelve Data API"

    assert (
        set(values_keys[0]) == twelvedata_api_config["timeseries_values_keys"]
    ), "Data value keys are not the expected ones, check Twelve Data API"

    df = pd.DataFrame(response_json["values"])
    df = df.astype(
        {
            "open": "float64",
            "high": "float64",
            "high": "float64",
            "close": "float64",
            "volume": "int64",
        }
    )
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime").sort_index()

    working_df: pd.Series = df["close"]

    return {
        "status": "ok",
        "exchange": exchange,
        "timezone": timzezone,
        "data": working_df,
    }


@handle_exception
def get_markets_state(api_key: str) -> Dict[str, str | int | pd.DataFrame]:
    """Retrieves market state from Twelve Data API.

    If request fails (not enough token), status is "ko"
    and df is None.
    If request succeds, status is "ok" and df contains the dataframe
    with columns name, country, is_market_open, time_to_open, time_to_close, time_after_open, date_check.

    Parameters
    ----------
    api_key : str
        API key for the Tweleve Data API.

    Returns
    -------
    Dict[str, str | int | pd.DataFrame]
        Dict[str, str | int | pd.DataFrame]
        res["status"] is ok or error
        If status is error, dict contains code of error and message
        If status is ok, dict contains market state dataframe

    Examples
    ----------

    If all goes right :

    >>> res = get_markets_state(API_KEY)
    >>> res['status']
    ok
    >>> res['data']
       exchange         country  isMarketOpen      timeToOpen     timeToClose
    0      NYSE   United States          True 0 days 00:00:00 0 days 02:56:09
    3    NASDAQ   United States          True 0 days 00:00:00 0 days 02:56:09

    If something went wrong :

    >>> get_markets_state(API_KEY)
    {"status": "error", "code": 500, "message": "Erreur"}

    See :func:`src.exceptions_twelvedata_api.handle_exception` for more informations on possible errors.

    """
    params = {"apikey": api_key}
    response = requests.get(twelvedata_api_config["market_url"], params=params)

    response_json = check_twelvedata_api_response(response)

    data: List[Dict[str, str | bool]] = check_type(
        response_json["data"], List[Dict[str, str | bool]]
    )

    assert data, "No data retrieved, check Twelve Data API."

    data_keys = [x.keys() for x in data]
    # Assert that data is of type List[Dict] with all dict having same keys
    assert all(
        x == data_keys[0] for x in data_keys
    ), "Data value keys are not always the same, check Twelve Data API."

    assert (
        set(data_keys[0]) == twelvedata_api_config["market_keys"]
    ), "Data value keys are not the expected ones, check Twelve Data API."

    df = pd.DataFrame(data).drop(columns=["code"]).drop_duplicates()
    df[["time_to_open", "time_to_close", "time_after_open"]] = df[
        ["time_to_open", "time_to_close", "time_after_open"]
    ].apply(pd.to_timedelta)

    df.rename(
        {
            "name": "exchange",
            "time_to_open": "timeToOpen",
            "time_to_close": "timeToClose",
            "is_market_open": "isMarketOpen",
            "time_after_open": "timeAfterOpen",
        },
        axis=1,
        inplace=True,
    )

    response_json["data"] = df

    return response_json
