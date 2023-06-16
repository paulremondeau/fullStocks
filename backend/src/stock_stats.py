#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""stock_stats.py:  function

This module contains all the statistics needed for stocks.
"""

__author__ = "Paul RÉMONDEAU"
__copyright__ = "Paul RÉMONDEAU"
__version__ = "1.0.0"
__maintainer__ = "Paul RÉMONDEAU"
__email__ = "paulremondeau@yahoo.fr"
__status__ = "Production"
__logger__ = "stocks_stats.py"

# =================================================================================================
#     Libs
# =================================================================================================

from typing import Dict

import numpy as np
import pandas as pd

from dateutil.relativedelta import relativedelta


# =================================================================================================
#     Functions
# =================================================================================================


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
        The stock symbol.

    Returns
    -------
    Dict[str, float | str]
        The result dict.

    Examples
    ----------

    >>> data = pd.Series(
    ...     [1, 5, 7, 2, 3],
    ...     index=pd.Index(
    ...         [
    ...             pd.Timestamp(0, unit="d"),
    ...             pd.Timestamp(7, unit="d"),
    ...             pd.Timestamp(3, unit="d"),
    ...             pd.Timestamp(4, unit="d"),
    ...             pd.Timestamp(365, unit="d"),
    ...         ]
    ...     ),
    ... )
    >>> evaluate_stats_information(data, "AAPL")
    {'symbol': 'AAPL', 'cumulativeReturn': -40.0, 'annualizedCumulativeReturn': 200.0, 'annualizedVolatility': 2.41}

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
