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
    """Wrapps the Twelve Data API for result quality checks.

    This function take care of all the exceptions concerning the data
    Twelve Data API data quality.

    Parameters
    ----------
    response : requests.Response
        The Twelve Data API response.

    Returns
    -------
    Dict[str, str | list]
        The dict of the app API.
        If no exception was raised, the return dict is like {"status": "ok", "data": "}
        If an exception was raised, returns a dict like {"status": "ko", "code": 500, "message": "Exception description"}

    Raises
    ------
    TwelveDataApiException
        Exception with the Twelve Data API
        code: the error code
        message: message related to the exception

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
def request_stock_time_series(
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

    return {"status": "ok", "exchange": exchange, "data": working_df}


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
            - if status is error, dict contains code of error and message
            - if status is ok, dict contains market state dataframe
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
