#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""utils.py:  function

This module contains various utility functions.
"""

__author__ = "Paul RÉMONDEAU"
__copyright__ = "Paul RÉMONDEAU"
__version__ = "1.0.0"
__maintainer__ = "Paul RÉMONDEAU"
__email__ = "paulremondeau@yahoo.fr"
__status__ = "Production"
__logger__ = "utils.py"

# =================================================================================================
#     Libs
# =================================================================================================

import json
from typing import List

import pandas as pd

# =================================================================================================
#     Exceptions
# =================================================================================================


def read_twelvedata_api_config_file(file_path: str):
    """Custome loading of twelvedata pi config file.

    This transforms list values whom keys end with '_keys'
    to set.

    Parameters
    ----------
    file_path : str
        The config file path.

    Examples
    ----------

    >>> import json
    >>> example_json = {"my_key": "foo", "my_keys": [1,2,3,4], "my_keys_not_working": [1,2,3,4], "not_a_list_keys": "foo"}
    >>> with open("config.json", "x") as f:
    >>>     json.dump(example_json, f)
    >>> read_twelvedata_api_config_file("config.json")
    {
     'my_key': 'foo',
     'my_keys': {1, 2, 3, 4},
     'my_keys_not_working': [1, 2, 3, 4],
     'not_a_list_keys': 'foo'
    }
    """

    def parse_for_keys(dct: dict):
        res: dict = {
            key: (
                set(value) if key[-5:] == "_keys" and isinstance(value, list) else value
            )
            for (key, value) in dct.items()
        }
        return res

    with open(file_path) as f:
        res = json.load(f, object_hook=parse_for_keys)

    return res


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

    Examples
    ----------
    >>> stock_time_series = [3, 1, 2]
    >>> stock_dates = [
    >>>     pd.Timestamp(1, unit="ms"),
    >>>     pd.Timestamp(2, unit="ms"),
    >>>     pd.Timestamp(3, unit="ms"),
    >>> ]
    >>> format_sending_data(stock_time_series, stock_dates, performance = False)
    [[1, 3], [2,1], [3, 2]]
    >>> format_sending_data(stock_time_series, stock_dates, performance = True)
    [[1, 100.0], [2, 33.33], [3, 66.67]]
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
