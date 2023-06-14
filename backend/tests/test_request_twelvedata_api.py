#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_request_twelvedata_api.py: tests

Contains unit tests for src.request_twelvedata_api.py"""

__author__ = "Paul Rémondeau"
__copyright__ = "Paul Rémondeau"
__version__ = "1.0.0"
__maintainer__ = "Paul Rémondeau"
__email__ = "paulremondeau@yahoo.fr"
__status__ = "Production"

# ===============================
#  Libs
# ===============================


import pytest

import os
import sys
import json

import pandas as pd

import requests_mock

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from src.request_twelvedata_api import (
    get_stock_timeseries,
    get_markets_state,
)

from src.utils import read_twelvedata_api_config_file

twelvedata_api_config_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "config",
    "twelvedata_api_info.json",
)

twelvedata_api_config = read_twelvedata_api_config_file(twelvedata_api_config_path)


def test_request_stock_time_series(requests_mock):
    # region Should handle exceptions

    # region Should handle status error from Twelve Data API
    api_response = {"status": "error", "code": 400, "message": "foo"}
    requests_mock.get(twelvedata_api_config["timeseries_url"], json=api_response)

    assert get_stock_timeseries("foo", "foo") == {
        "status": "error",
        "code": 400,
        "message": "foo",
    }
    # endregion

    # region Should handle when data type are not correct

    # region Should handle when meta data is not Dict[str, str]
    meta = {
        "foo": 1,
    }
    values = []

    api_response = {"meta": meta, "values": values, "status": "ok"}
    requests_mock.get(twelvedata_api_config["timeseries_url"], json=api_response)
    assert get_stock_timeseries("foo", "foo") == {
        "code": 500,
        "message": "value of key 'foo' of dict is not an instance of str",
        "status": "error",
    }
    # endregion

    # region Should handle when values is not List[Dict[str, str]]
    meta = {
        "foo": "foo",
    }

    values = [[]]
    api_response = {"meta": meta, "values": values, "status": "ok"}
    requests_mock.get(twelvedata_api_config["timeseries_url"], json=api_response)
    assert get_stock_timeseries("foo", "foo") == {
        "code": 500,
        "message": "item 0 of list is not a dict",
        "status": "error",
    }

    values = [{"datetime": 123456789}]
    api_response = {"meta": meta, "values": values, "status": "ok"}
    requests_mock.get(twelvedata_api_config["timeseries_url"], json=api_response)
    assert get_stock_timeseries("foo", "foo") == {
        "code": 500,
        "message": "value of key 'datetime' of item 0 of list is not an instance of str",
        "status": "error",
    }

    # endregion

    # endregion

    # region Should handle when assertions are false

    # region Should handle if meta keys are not correct
    meta = {
        "foo": "foo",
        "interval": "1min",
        "currency": "USD",
        "exchange_timezone": "America/New_York",
        "exchange": "NASDAQ",
        "mic_code": "XNAS",
        "type": "Common Stock",
    }
    values = []

    api_response = {"meta": meta, "values": values, "status": "ok"}
    requests_mock.get(twelvedata_api_config["timeseries_url"], json=api_response)
    assert get_stock_timeseries("foo", "foo") == {
        "status": "error",
        "code": 500,
        "message": "Meta data are not correct, check Twelve Data API",
    }
    # endregion

    # region Should handle if values is empty
    meta = {
        "symbol": "AAPL",
        "interval": "1min",
        "currency": "USD",
        "exchange_timezone": "America/New_York",
        "exchange": "NASDAQ",
        "mic_code": "XNAS",
        "type": "Common Stock",
    }
    values = []
    api_response = {"meta": meta, "values": values, "status": "ok"}
    requests_mock.get(twelvedata_api_config["timeseries_url"], json=api_response)
    assert get_stock_timeseries("foo", "foo") == {
        "status": "error",
        "code": 500,
        "message": "Data value is empty, check Twelve Data API",
    }
    # endregion

    # region Should handle if values contains dicts with not the same keys
    meta = {
        "symbol": "AAPL",
        "interval": "1min",
        "currency": "USD",
        "exchange_timezone": "America/New_York",
        "exchange": "NASDAQ",
        "mic_code": "XNAS",
        "type": "Common Stock",
    }

    values = [
        {
            "dateime": "2021-09-16 15:59:00",
            "open": "148.73500",
            "high": "148.86000",
        },
        {
            "datetime": "2021-09-16 15:58:00",
            "open": "148.72000",
            "high": "148.78000",
        },
    ]
    api_response = {"meta": meta, "values": values, "status": "ok"}
    requests_mock.get(twelvedata_api_config["timeseries_url"], json=api_response)
    assert get_stock_timeseries("foo", "foo") == {
        "status": "error",
        "code": 500,
        "message": "Data value keys are not always the same, check Twelve Data API",
    }
    # endregion

    # region Should handle if values contains dicts with not the expected keys
    values = [
        {
            "datetime": "2021-09-16 15:59:00",
            "open": "148.73500",
            "high": "148.86000",
        },
        {
            "datetime": "2021-09-16 15:58:00",
            "open": "148.72000",
            "high": "148.78000",
        },
    ]
    api_response = {"meta": meta, "values": values, "status": "ok"}
    requests_mock.get(twelvedata_api_config["timeseries_url"], json=api_response)
    assert get_stock_timeseries("foo", "foo") == {
        "status": "error",
        "code": 500,
        "message": "Data value keys are not the expected ones, check Twelve Data API",
    }
    # endregion

    # endregion

    # endregion

    # region Sould correctly convert data from Twelve Data API
    meta = {
        "symbol": "AAPL",
        "interval": "1min",
        "currency": "USD",
        "exchange_timezone": "America/New_York",
        "exchange": "NASDAQ",
        "mic_code": "XNAS",
        "type": "Common Stock",
    }

    values = [
        {
            "datetime": "2021-09-16 15:59:00",
            "open": "148.73500",
            "high": "148.86000",
            "low": "148.73000",
            "close": "148.85001",
            "volume": "624277",
        },
        {
            "datetime": "2021-09-16 15:58:00",
            "open": "148.72000",
            "high": "148.78000",
            "low": "148.70000",
            "close": "148.74001",
            "volume": "274622",
        },
    ]
    api_response = {"meta": meta, "values": values, "status": "ok"}

    requests_mock.get(twelvedata_api_config["timeseries_url"], json=api_response)

    target_df = pd.Series(
        [148.74001, 148.85001],
        index=pd.Index(
            [
                pd.to_datetime("2021-09-16 15:58:00"),
                pd.to_datetime("2021-09-16 15:59:00"),
            ],
            name="datetime",
        ),
        name="close",
        dtype="float64",
    )

    result = get_stock_timeseries("foo", "foo")
    assert set(result.keys()) == {"status", "exchange", "timezone", "data"}
    print(result)

    result_status = result["status"]
    assert result_status == "ok"

    result_exchange = result["exchange"]
    assert result_exchange == "NASDAQ"

    result_timezone = result["timezone"]
    assert result_timezone == "America/New_York"

    result_df = result["data"]
    assert result_df.equals(target_df)
    # endregion


def test_get_markets_state(requests_mock):
    # region Should handle exceptions

    # region Should handle status error from Twelve Data API
    api_response = {"status": "error", "code": 400, "message": "foo"}
    requests_mock.get(twelvedata_api_config["market_url"], json=api_response)

    assert get_markets_state("foo") == {
        "status": "error",
        "code": 400,
        "message": "foo",
    }
    # endregion

    # region Should handle when data type are not correct

    # region Should handle when meta data is not Dict[str, str]
    data = [{"foo": 1}]

    api_response = {"data": data, "status": "ok"}
    requests_mock.get(twelvedata_api_config["market_url"], json=api_response)
    assert get_markets_state("foo") == {
        "code": 500,
        "message": "value of key 'foo' of item 0 of list did not match any element in the union:\n  str: is not an instance of str\n  bool: is not an instance of bool",
        "status": "error",
    }
    # endregion

    # region Should handle when data is empty

    data = []

    api_response = {"data": data, "status": "ok"}
    requests_mock.get(twelvedata_api_config["market_url"], json=api_response)
    assert get_markets_state("foo") == {
        "code": 500,
        "message": "No data retrieved, check Twelve Data API.",
        "status": "error",
    }

    # endregion

    # region Should handle when data keys are not consistent

    data = [{"key1": "ok"}, {"key2": "ok"}]

    api_response = {"data": data, "status": "ok"}
    requests_mock.get(twelvedata_api_config["market_url"], json=api_response)
    assert get_markets_state("foo") == {
        "code": 500,
        "message": "Data value keys are not always the same, check Twelve Data API.",
        "status": "error",
    }

    # endregion

    # region Should handle whenn data keys are not the expected ones

    data = [{"key1": "ok"}, {"key1": "ok"}]

    api_response = {"data": data, "status": "ok"}
    requests_mock.get(twelvedata_api_config["market_url"], json=api_response)
    assert get_markets_state("foo") == {
        "code": 500,
        "message": "Data value keys are not the expected ones, check Twelve Data API.",
        "status": "error",
    }

    # endregion

    # endregion

    # endregion

    # region Sould correctly convert data from Twelve Data API

    data = [
        {
            "name": "FOO1",
            "code": "1234",
            "country": "MOON",
            "is_market_open": True,
            "time_to_open": "00:00:00",
            "time_to_close": "01:00:00",
            "time_after_open": "04:00:00",
        },
        {
            "name": "FOO2",
            "code": "8456",
            "country": "EARTH",
            "is_market_open": False,
            "time_to_open": "04:00:00",
            "time_to_close": "00:00:00",
            "time_after_open": "00:00:00",
        },
    ]

    target_df = pd.DataFrame(
        [
            {
                "exchange": "FOO1",
                "country": "MOON",
                "isMarketOpen": True,
                "timeToOpen": pd.to_timedelta("00:00:00"),
                "timeToClose": pd.to_timedelta("01:00:00"),
                "timeAfterOpen": pd.to_timedelta("04:00:00"),
            },
            {
                "exchange": "FOO2",
                "country": "EARTH",
                "isMarketOpen": False,
                "timeToOpen": pd.to_timedelta("04:00:00"),
                "timeToClose": pd.to_timedelta("00:00:00"),
                "timeAfterOpen": pd.to_timedelta("00:00:00"),
            },
        ]
    )

    api_response = {"data": data, "status": "ok"}
    requests_mock.get(twelvedata_api_config["market_url"], json=api_response)

    response_json = get_markets_state("foo")
    response_status = response_json["status"]
    response_df = response_json["data"]

    assert response_status == "ok"
    assert target_df.equals(response_df)

    # endregion
