#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""exceptions_twelvedata_api.py:  function, exception

This module manages exceptions from Twelve Data API.
"""

__author__ = "Paul RÉMONDEAU"
__copyright__ = "Paul RÉMONDEAU"
__version__ = "1.0.0"
__maintainer__ = "Paul RÉMONDEAU"
__email__ = "paulremondeau@yahoo.fr"
__status__ = "Production"
__logger__ = "exceptions_twelvedata_api.py"

# =================================================================================================
#     Libs
# =================================================================================================

from typeguard import TypeCheckError

# =================================================================================================
#     Functions
# =================================================================================================


class TwelveDataApiException(Exception):
    """Exception class for issues coming from Twelve Data API."""

    def __init__(self, code, message):
        self.code = code
        self.message = message


def handle_exception(func):
    """Wrapper for exceptions handling.

    This wrapper catch exceptions.

    Parameters
    ----------
    func : _type_
        _description_
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except TwelveDataApiException as e:
            return {"status": "error", "code": e.code, "message": e.message}

        except AssertionError as e:
            return {"status": "error", "code": 500, "message": e.args[0]}

        except TypeCheckError as e:
            return {"status": "error", "code": 500, "message": str(e)}

    return wrapper
