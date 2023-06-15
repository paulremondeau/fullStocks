#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_utils.py: test

Contains unit tests for src.utils"""

__author__ = "Paul Rémondeau"
__copyright__ = "Paul Rémondeau"
__version__ = "1.0.0"
__maintainer__ = "Paul Rémondeau"
__email__ = "paulremondeau@yahoo.fr"
__status__ = "Dev"

# ===============================
#  Libs
# ===============================


import pytest

import os
import json
import sys

import numpy as np
import pandas as pd

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from src.utils import series_to_apexcharts, read_twelvedata_api_config_file

# ===============================
#  Tests
# ===============================


def test_series_to_apexcharts():
    # Should return None if one of the parameters is None
    assert series_to_apexcharts(None, "foo") == []

    # Should return an empty list if input data are empty lists
    stock_dates = []
    stock_time_series = []
    timeseries = pd.Series(stock_time_series, index=stock_dates)
    assert series_to_apexcharts(timeseries) == []

    # Should return data correctly in either performance or normal mode
    stock_dates = [
        pd.Timestamp(1, unit="ms"),
        pd.Timestamp(2, unit="ms"),
        pd.Timestamp(3, unit="ms"),
    ]
    stock_time_series = [3, 1, 2]
    timeseries = pd.Series(stock_time_series, index=stock_dates)
    assert series_to_apexcharts(timeseries) == [
        [1, 100.0],
        [2, 33.33],
        [3, 66.67],
    ]

    assert series_to_apexcharts(timeseries, performance=False) == [
        [1, 3],
        [2, 1],
        [3, 2],
    ]


def test_read_twelvedata_api_config_file():
    example_json = {
        "my_key": "foo",
        "my_keys": [1, 2, 3, 4],
        "my_keys_not_working": [1, 2, 3, 4],
        "not_a_list_keys": "foo",
    }
    with open("temp_for_read_twelvedata_api_config_file.json", "x") as f:
        json.dump(example_json, f)

    assert read_twelvedata_api_config_file(
        "temp_for_read_twelvedata_api_config_file.json"
    ) == {
        "my_key": "foo",
        "my_keys": {1, 2, 3, 4},
        "my_keys_not_working": [1, 2, 3, 4],
        "not_a_list_keys": "foo",
    }

    os.remove("temp_for_read_twelvedata_api_config_file.json")
