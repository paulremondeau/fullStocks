#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_stock_stats.py: test

Contains unit tests for src.stock_stats"""

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

import numpy as np
import pandas as pd

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from src.stock_stats import (
    evaluate_cumulative_return,
    evaluate_annualized_return,
    evaluate_stats_information,
)

# ===============================
#  Tests
# ===============================


def test_evaluate_cumulative_return():
    # Should return nan if not enough data
    data = pd.Series(
        [1],
        index=pd.Index(
            [
                pd.Timestamp(1, unit="d"),
            ]
        ),
    )
    assert evaluate_cumulative_return(data) == "-"

    # Should work if data is good
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
    # Should return nan if data is not timely wide enough

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
    assert evaluate_annualized_return(data, n_years=1) == "-"

    data = pd.Series(
        [1, 5, 7, 2, 3],
        index=pd.Index(
            [
                pd.Timestamp(0, unit="d"),
                pd.Timestamp(7, unit="d"),
                pd.Timestamp(3, unit="d"),
                pd.Timestamp(4, unit="d"),
                pd.Timestamp(365, unit="d"),
            ]
        ),
    )
    assert evaluate_annualized_return(data, n_years=2) == "-"

    # Should work if data is timely wide enough
    assert evaluate_annualized_return(data, n_years=1) == 200.0


# TODO : complete this
def test_evaluate_annualized_volatility():
    pass


def test_evaluate_stats_information():
    symbol = "foo"
    data = pd.Series(
        [1, 5, 7, 2, 3],
        index=pd.Index(
            [
                pd.Timestamp(0, unit="d"),
                pd.Timestamp(7, unit="d"),
                pd.Timestamp(3, unit="d"),
                pd.Timestamp(4, unit="d"),
                pd.Timestamp(365, unit="d"),
            ]
        ),
    )

    assert evaluate_stats_information(data, symbol) == {
        "symbol": symbol,
        "cumulativeReturn": -40.0,
        "annualizedCumulativeReturn": 200.0,
        "annualizedVolatility": 2.41,
    }
