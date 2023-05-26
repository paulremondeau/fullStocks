import requests
import json
from copy import copy
from typing import List, Tuple, Dict

import pandas as pd
from dateutil.relativedelta import relativedelta

from config import API_KEY

URL_TIMESERIES = "https://api.twelvedata.com/time_series"
PARAMS_TIMESERIES = {
    "apikey": API_KEY,
    "interval": "8h",
    "outputsize": "5000",
    "format": "json",
}

URL_SYMBOLS = "https://api.twelvedata.com/stocks"
PARAMS_SYMBOLS = {"apikey": API_KEY, "format": "json"}


def request_stock_time_series(
    symbol: str,
) -> Tuple[Dict[str, float], Dict[str, Dict[str, float]]]:
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
    Tuple[Dict, Dict[str, Dict[str, float]]]
        The first dictionnary is the time series data.
        The second dictionnary contains the statistics data.
    """

    # API request
    params = copy(PARAMS_TIMESERIES)
    params["symbol"] = symbol
    response = requests.get(URL_TIMESERIES, params=params)

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
    working_df = working_df.rename(symbol)

    # Cumulative return as (f(t) - f(t-1))/f(t-1) *100
    cumulative_return: float = (
        (working_df.iloc[-1] - working_df.iloc[-2]) / working_df.iloc[-2] * 100
    )
    cumulative_return = float(f"{cumulative_return:.2f}")

    # Annualized cumulative return
    stock_price_one_year_ago: float = working_df[
        working_df.index >= (working_df.index[-1] - relativedelta(years=1))
    ].iloc[0]
    annualized_cumulative_return: float = (
        (working_df.iloc[-1] - stock_price_one_year_ago)
        / stock_price_one_year_ago
        * 100
    )
    annualized_cumulative_return = float(f"{annualized_cumulative_return:.2f}")

    # Annualized volatility
    annualized_volatility: float = (
        working_df[working_df.index >= working_df.index[-1] - relativedelta(years=1)]
    ).std()
    annualized_volatility = float(f"{annualized_volatility:.2f}")

    json_stats: Dict[str, Dict[str, float]] = {
        "symbol": symbol,
        "cumulativeReturn": cumulative_return,
        "annualizedCumulativeReturn": annualized_cumulative_return,
        "annualizedVolatility": annualized_volatility,
    }

    # Performance
    performance_df = working_df / working_df.iloc[0] * 100
    performance_json: Dict[str, float] = json.loads(performance_df.to_json())

    return performance_json, json_stats


def request_avalaible_symbols(exchange: List[str] = ["NASDAQ"]) -> List[str]:
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
    response = requests.get(URL_SYMBOLS, params=params)

    symbols_list: List[str] = [x["symbol"] for x in response.json()["data"]]
    return symbols_list
