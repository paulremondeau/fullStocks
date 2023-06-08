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
import sys

import pandas as pd

import requests_mock

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from src.utils import (
    request_stock_time_series,
    URL_TIMESERIES,
    # get_stocks_list,
    URL_SYMBOLS,
    format_sending_data,
    evaluate_cumulative_return,
    evaluate_annualized_return,
    evaluate_annualized_volatility,
    evaluate_stats_information,
    get_markets_state,
    URL_MARKET_STATE,
)

# ===============================
#  Tests
# ===============================


def test_request_stock_time_series(requests_mock):
    # region Should handle exceptions

    # region Should handle status error from Twelve Data API
    api_response = {"status": "error", "code": 400, "message": "foo"}
    requests_mock.get(URL_TIMESERIES, json=api_response)

    assert request_stock_time_series("foo", "foo") == {
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
    requests_mock.get(URL_TIMESERIES, json=api_response)
    assert request_stock_time_series("foo", "foo") == {
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
    requests_mock.get(URL_TIMESERIES, json=api_response)
    assert request_stock_time_series("foo", "foo") == {
        "code": 500,
        "message": "item 0 of list is not a dict",
        "status": "error",
    }

    values = [{"datetime": 123456789}]
    api_response = {"meta": meta, "values": values, "status": "ok"}
    requests_mock.get(URL_TIMESERIES, json=api_response)
    assert request_stock_time_series("foo", "foo") == {
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
    requests_mock.get(URL_TIMESERIES, json=api_response)
    assert request_stock_time_series("foo", "foo") == {
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
    requests_mock.get(URL_TIMESERIES, json=api_response)
    assert request_stock_time_series("foo", "foo") == {
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
    requests_mock.get(URL_TIMESERIES, json=api_response)
    assert request_stock_time_series("foo", "foo") == {
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
    requests_mock.get(URL_TIMESERIES, json=api_response)
    assert request_stock_time_series("foo", "foo") == {
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

    requests_mock.get(URL_TIMESERIES, json=api_response)

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

    result = request_stock_time_series("foo", "foo")
    result_status = result["status"]
    result_exchange = result["exchange"]
    result_df = result["data"]

    assert result_status, result_exchange == ("ok", "NASDAQ")
    assert result_df.equals(target_df)
    # endregion


# def test_get_stocks_list():
#     pass


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
    stock_time_series = [1, 2, 3]
    assert format_sending_data(stock_dates, stock_time_series) == [
        [1, 100.0],
        [2, 200.0],
        [3, 300.0],
    ]

    assert format_sending_data(stock_dates, stock_time_series, performance=False) == [
        [1, 1],
        [2, 2],
        [3, 3],
    ]


def test_evaluate_cumulative_return():
    data = pd.Series(
        [1, 5, 7, 2, 3],
        index=pd.Index(
            [
                pd.Timestamp(1, unit="d"),
                pd.Timestamp(7, unit="d"),
                pd.Timestamp(3, unit="d"),
                pd.Timestamp(4, unit="d"),
                pd.Timestamp(5, unit="d"),
            ]
        ),
    )

    assert evaluate_cumulative_return(data) == 66.67


def test_evaluate_annualized_return():
    pass


def test_evaluate_annualized_volatility():
    pass