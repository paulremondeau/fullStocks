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
    def parse_for_keys(dct: dict):
        res: dict = {
            key: (set(value) if key[-5:] == "_keys" else value)
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
