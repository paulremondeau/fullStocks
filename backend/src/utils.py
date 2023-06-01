import requests
import json
from copy import copy
from typing import List, Tuple, Dict

import pandas as pd
from dateutil.relativedelta import relativedelta


URL_TIMESERIES = "https://api.twelvedata.com/time_series"
PARAMS_TIMESERIES = {
    "interval": "8h",
    "outputsize": "5000",
    "format": "json",
}

URL_SYMBOLS = "https://api.twelvedata.com/stocks"
PARAMS_SYMBOLS = {"format": "json"}

URL_MARKET_STATE = "https://api.twelvedata.com/market_state"


def request_stock_time_series(
    symbol: str, api_key: str
) -> Tuple[str, Dict[str, float], Dict[str, Dict[str, float]]]:
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
    Tuple[str, Dict, Dict[str, Dict[str, float]]]
        The str is the twelve data API call status.
        The first dictionnary is the time series data.
        The second dictionnary contains the statistics data.
    """

    # API request
    params = copy(PARAMS_TIMESERIES)
    params["symbol"] = symbol
    params["apikey"] = api_key
    response = requests.get(URL_TIMESERIES, params=params)

    status = response.json()["status"]

    if status == "error":
        # The request failed
        return status, None

    elif status == "ok":
        # Convert to dataframe for easier manipulation
        df = pd.DataFrame(response.json()["values"])
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

        return status, working_df


def request_avalaible_symbols(
    api_key: str, exchange: List[str] = ["NASDAQ"]
) -> List[str]:
    """Fetch the available symbols list.

    This function fetch the twelvedata API to get
    the symbols of the instruments exchanged on
    specifics exchange place.

    Parameters
    ----------
    exchange : List[str], optional
        List of the exchanges place to fetch, by default ["NASDAQ"]

    Returns
    -------
    List[str]
        The symbols list
    """
    params = copy(PARAMS_SYMBOLS)
    if exchange:
        params["exchange"] = exchange
    params["apikey"] = api_key
    response = requests.get(URL_SYMBOLS, params=params)

    symbols_list: List[str] = [x["symbol"] for x in response.json()["data"]]
    return symbols_list


def format_sending_data(
    stock_dates: List[pd.Timestamp] | None,
    stock_time_series: List[float] | None,
    performance: bool = True,
) -> List[list]:
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
    List[list] | None
        The data formatted.
    """
    if stock_dates is None or stock_time_series is None:
        return None

    else:
        stocks_date_timestamps = [
            int(date_value.timestamp() * 1000) for date_value in stock_dates
        ]

        if performance:
            stock_time_series = list(
                pd.Series(stock_time_series) / stock_time_series[0] * 100
            )

        result = [
            [timestamp, float(f"{ts_value:.2f}")]
            for timestamp, ts_value in zip(stocks_date_timestamps, stock_time_series)
        ]

        return result


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
    # Cumulative return as (f(t) - f(t-1))/f(t-1) *100
    cumulative_return: float = (data.iloc[-1] - data.iloc[-2]) / data.iloc[-2] * 100
    cumulative_return = float(f"{cumulative_return:.2f}")

    # Annualized cumulative return
    stock_price_one_year_ago: float = data[
        data.index >= (data.index[-1] - relativedelta(years=1))
    ].iloc[0]
    annualized_cumulative_return: float = (
        (data.iloc[-1] - stock_price_one_year_ago) / stock_price_one_year_ago * 100
    )
    annualized_cumulative_return = float(f"{annualized_cumulative_return:.2f}")

    # Annualized volatility
    annualized_volatility: float = (
        data[data.index >= data.index[-1] - relativedelta(years=1)]
    ).std()
    annualized_volatility = float(f"{annualized_volatility:.2f}")

    json_stats: Dict[str, Dict[str, float]] = {
        "symbol": symbol,
        "cumulativeReturn": cumulative_return,
        "annualizedCumulativeReturn": annualized_cumulative_return,
        "annualizedVolatility": annualized_volatility,
    }

    return json_stats


def get_markets_state(api_key: str) -> pd.DataFrame:
    params = {"apikey": api_key}
    response = requests.get(URL_MARKET_STATE, params=params)

    return
