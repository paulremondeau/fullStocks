import requests
import json
from copy import copy
from typing import List, Tuple, Dict

import numpy as np
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

from typeguard import check_type

from .exceptions import TwelveDataApiException, handle_exception


URL_TIMESERIES = "https://api.twelvedata.com/time_series"
PARAMS_TIMESERIES = {
    "interval": "8h",
    "outputsize": "5000",
    "format": "json",
}
META_KEYS = {
    "symbol",
    "interval",
    "currency",
    "exchange_timezone",
    "exchange",
    "mic_code",
    "type",
}
VALUES_KEYS = {
    "datetime",
    "open",
    "high",
    "low",
    "volume",
    "close",
}


URL_SYMBOLS = "https://api.twelvedata.com/stocks"

URL_MARKET_STATE = "https://api.twelvedata.com/market_state"
MARKET_STATE_KEYS = {
    "name",
    "code",
    "country",
    "is_market_open",
    "time_to_open",
    "time_to_close",
    "time_after_open",
}


# TODO :  docstring this
def check_twelvedata_api_response(response: requests.Response) -> Dict[str, str | list]:
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
    params = copy(PARAMS_TIMESERIES)
    params["symbol"] = symbol
    params["apikey"] = api_key
    response = requests.get(URL_TIMESERIES, params=params)

    response_json = check_twelvedata_api_response(response)

    meta: Dict[str, str] = check_type(response_json["meta"], Dict[str, str])

    values: List[Dict[str, str]] = check_type(
        response_json["values"], List[Dict[str, str]]
    )

    # Assert meta data is good format
    assert (
        set(meta.keys()) == META_KEYS
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
        set(values_keys[0]) == VALUES_KEYS
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


# def get_stocks_list(api_key: str, exchanges: List[str]) -> List[str]:
#     """Fetch the available stocks list.

#     This function fetch the twelvedata API to get
#     the symbols of the stocks available on the API.
#     Note : the available stocks depends on your Twelve
#     Data bill plan.

#     Parameters
#     ----------
#     exchanges : List[str]
#         List of the exchanges needed.

#     Returns
#     -------
#     List[str]
#         The symbols list
#     """
#     params = {"apikey": api_key}
#     params["exchange"] = exchanges
#     params["apikey"] = api_key
#     response = requests.get(URL_SYMBOLS, params=params)

#     symbols_list: List[str] = [x["symbol"] for x in response.json()["data"]]
#     return symbols_list


def format_sending_data(
    stock_dates: List[pd.Timestamp] | None,
    stock_time_series: List[float] | None,
    performance: bool = True,
) -> List[List[int | float]]:
    """Format data to send to the frontend.

    This function pre-process the data before sending to
    the front-end. The goal is to match the apexcharts line chart
    format, where a point is [12345, 1.0].

    Parameters
    ----------
    stock_dates : List[pd.Timestamp] | None
        The timestamps data.
    stock_time_series : List[float] | None
        The stock values data.
    performance : bool, optional
        If true, transforms data to create performance data, by
        default True

    Returns
    -------
    List[List[int | float]]
        The data formatted.
    """

    if stock_dates is None or stock_time_series is None:
        result = []

    else:
        stocks_date_timestamps = [
            int(date_value.timestamp() * 1000) for date_value in stock_dates
        ]

        if performance:
            # Format for performance
            try:
                stock_time_series = list(
                    pd.Series(stock_time_series) / stock_time_series[0] * 100
                )
            except IndexError:
                stock_time_series = []

        result = [
            [timestamp, float(f"{ts_value:.2f}")]
            for timestamp, ts_value in zip(stocks_date_timestamps, stock_time_series)
        ]

    return result


def evaluate_cumulative_return(data: pd.Series) -> float:
    """Evaluate the cumulative return of a series in percent.

    Lets write P_initial the initial value of our series,
    and P_current the current value of our series.

    The cumulative return is then (P_current - P_initial) / P_initial


    Parameters
    ----------
    data : pd.Series
        The data series of stock price.

    Returns
    -------
    float
        The cumulative return.
        If data is not long enough, return np.nan.
    """

    if not data.index.is_monotonic_increasing:
        data = data.sort_index()

    if len(data) < 2:
        cumulative_return = np.nan

    else:
        cumulative_return: float = (data[-1] - data[-2]) / data[-2] * 100
        cumulative_return = float(f"{cumulative_return:.2f}")

    return cumulative_return


def evaluate_annualized_return(data: pd.Series, n_years: int) -> float:
    """Evaluate the annualized return.

    The annualized return for n_years is
    ((1+ Rc) ^ (1/n_years)) - 1

    Parameters
    ----------
    data : pd.Series
        The data series of stock price.
    n_years: int
        The number of years we want to calculate the return for.

    Returns
    -------
    float
        The annualized cumulative return.
        If data is not long enough, return np.nan.
    """
    if not data.index.is_monotonic_increasing:
        data = data.sort_index()

    most_recent_date = data.index[-1]
    data_n_years_ago = data[
        data.index <= (most_recent_date - relativedelta(years=n_years))
    ]

    if data_n_years_ago.empty:
        # Stock price is not long enough to evaluate the annualized return for this n_years
        annualized_cumulative_return = np.nan

    else:
        stock_price_n_years_ago = data_n_years_ago[-1]

        cumulative_return: float = (
            data[-1] - stock_price_n_years_ago
        ) / stock_price_n_years_ago

        annualized_cumulative_return = (
            ((1 + cumulative_return) ** (1 / n_years)) - 1
        ) * 100
        annualized_cumulative_return = float(f"{annualized_cumulative_return:.2f}")

    return annualized_cumulative_return


# TODO: review this
def evaluate_annualized_volatility(data: pd.Series, n_years: int = 1) -> float:
    """Evaluate the annualized volatility.

    Parameters
    ----------
    data : pd.Series
        The data.
    n_years: int
        The number of years we want to calculate the volatility for.

    Returns
    -------
    float
        The annualized volatility.
    """

    annualized_volatility: float = (
        data[data.index >= data.index[-1] - relativedelta(years=1)]
    ).std()
    annualized_volatility = float(f"{annualized_volatility:.2f}")

    return annualized_volatility


def evaluate_stats_information(data: pd.Series, symbol: str) -> Dict[str, float | str]:
    """Gives several statistics about stock time-series.

    This function evaluates several statistics about a
    stock time-series. The statistics are:
    - cumulative return
    - annualized cumulative return
    - annualized volatility

    Parameters
    ----------
    data : pd.Series
        The data, sorted in ascending time.

    symbol : str
        The stock symbol

    Returns
    -------
    Dict[str, float | str]
        The result dict.
    """

    cumulative_return: float = evaluate_cumulative_return(data)

    annualized_cumulative_return = evaluate_annualized_return(data, n_years=1)

    annualized_volatility: float = evaluate_annualized_volatility(data)

    json_stats: Dict[str, Dict[str, float]] = {
        "symbol": symbol,
        "cumulativeReturn": cumulative_return,
        "annualizedCumulativeReturn": annualized_cumulative_return,
        "annualizedVolatility": annualized_volatility,
    }

    return json_stats


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
    response = requests.get(URL_MARKET_STATE, params=params)

    response_json = check_twelvedata_api_response(response)

    data: List[Dict[str, str]] = check_type(response_json["data"], List[Dict[str, str]])

    assert data, "No data retrieved, check Twelve Data API."

    # TODO : finish this
    # data_keys = [x.keys() for x in data]
    # # Assert that data is of type List[Dict] with all dict having same keys
    # assert all(
    #     x == data_keys[0] for x in data_keys
    # ), "Data value keys are not always the same, check Twelve Data API"

    # assert (
    #     set(data_keys[0]) == VALUES_KEYS
    # ), "Data value keys are not the expected ones, check Twelve Data API"

    df = pd.DataFrame(data).drop(columns=["code"]).drop_duplicates()
    df[["time_to_open", "time_to_close", "time_after_open"]] = df[
        ["time_to_open", "time_to_close", "time_after_open"]
    ].apply(pd.to_timedelta)
    df["date_check"] = datetime.datetime.now()
    df.rename(
        {
            "name": "exchange",
            "time_to_open": "timeToOpen",
            "time_to_close": "timeToClose",
            "is_market_open": "isMarketOpen",
            "date_check": "dateCheck",
        },
        axis=1,
        inplace=True,
    )

    response_json["data"] = df

    return response_json
