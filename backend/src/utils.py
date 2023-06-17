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
from copy import deepcopy

import pandas as pd

# =================================================================================================
#     Exceptions
# =================================================================================================


# TODO : doctest is ugly...
def read_twelvedata_api_config_file(file_path: str):
    """Custom loading of twelvedata pi config file.

    This transforms list values whom keys end with '_keys'
    to set.

    Parameters
    ----------
    file_path : str
        The config file path.

    Examples
    ----------

    >>> import pprint
    >>> pprint.pprint((read_twelvedata_api_config_file("config/twelvedata_api_info.json")))
    {'market_keys': {'code',
                     'country',
                     'is_market_open',
                     'name',
                     'time_after_open',
                     'time_to_close',
                     'time_to_open'},
     'market_url': 'https://api.twelvedata.com/market_state',
     'symbols_url': 'https://api.twelvedata.com/stocks',
     'timeseries_meta_keys': {'currency',
                              'exchange',
                              'exchange_timezone',
                              'interval',
                              'mic_code',
                              'symbol',
                              'type'},
     'timeseries_params': {'format': 'json',
                           'interval': '8h',
                           'outputsize': '5000'},
     'timeseries_url': 'https://api.twelvedata.com/time_series',
     'timeseries_values_keys': {'close',
                                'datetime',
                                'high',
                                'low',
                                'open',
                                'volume'}}
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


def series_to_apexcharts(
    timeseries: pd.Series | None,
    performance: bool = True,
) -> List[List[int | float]]:
    """Format data to send to the frontend.

    This function transforms a pd.Series into a readable
    input for Apexcharts (frontend).

    Parameters
    ----------
    timeseries : pd.Series | None
        The timeseries.
    performance : bool, optional
        If true, transforms data to create performance data, by
        default True

    Returns
    -------
    List[List[int | float]]
        The data formatted.

    Examples
    ----------
    >>> import datetime
    >>> values = [3, 1, 2]
    >>> dates = [
    ...     datetime.datetime(2023, 1, 1),
    ...     datetime.datetime(2023, 1, 3),
    ...     datetime.datetime(2023, 1, 2),
    ... ]
    >>> timeseries = pd.Series(values, index = dates)
    >>> series_to_apexcharts(timeseries, performance = False)
    [[1672531200000, 3.0], [1672704000000, 1.0], [1672617600000, 2.0]]
    >>> series_to_apexcharts(timeseries, performance = True)
    [[1672531200000, 100.0], [1672704000000, 33.33], [1672617600000, 66.67]]
    """
    # print(timeseries)
    result = deepcopy(timeseries)

    if timeseries is None:
        result = []

    else:
        result = [
            [
                int(index.timestamp() * 1000),
                (
                    float(f"{value / result[0] * 100:.2f}")
                    if performance
                    else float(f"{value:.2f}")
                ),
            ]
            for index, value in result.items()
        ]

    return result
