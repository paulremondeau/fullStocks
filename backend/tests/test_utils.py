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

from src.utils import format_sending_data, read_twelvedata_api_config_file

# ===============================
#  Tests
# ===============================


def test_format_sending_data():
    # Should return None if one of the parameters is None
    assert format_sending_data(None, "foo", "foo") == []
    assert format_sending_data("foo", None, "foo") == []

    # Should return an empty list if input data are empty lists
    stock_dates = []
    stock_time_series = []
    assert format_sending_data(stock_dates, stock_time_series) == []

    # Should return data correctly if one data list is shorter than the other
    stock_dates = [pd.Timestamp(1, unit="ms"), pd.Timestamp(2, unit="ms")]
    stock_time_series = [1, 2, 3]
    assert format_sending_data(stock_dates, stock_time_series) == [
        [1, 100.0],
        [2, 200.0],
    ]

    stock_dates = [
        pd.Timestamp(1, unit="ms"),
        pd.Timestamp(2, unit="ms"),
        pd.Timestamp(3, unit="ms"),
    ]
    stock_time_series = [1, 2]
    assert format_sending_data(stock_dates, stock_time_series) == [
        [1, 100.0],
        [2, 200.0],
    ]

    # Should return data correctly in either performance or normal mode
    stock_dates = [
        pd.Timestamp(1, unit="ms"),
        pd.Timestamp(2, unit="ms"),
        pd.Timestamp(3, unit="ms"),
    ]
    stock_time_series = [3, 1, 2]
    assert format_sending_data(stock_dates, stock_time_series) == [
        [1, 100.0],
        [2, 33.33],
        [3, 66.67],
    ]

    assert format_sending_data(stock_dates, stock_time_series, performance=False) == [
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
