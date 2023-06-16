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

import functools

from typeguard import TypeCheckError

import logging

logger = logging.getLogger(__logger__)

# =================================================================================================
#     Functions
# =================================================================================================


class TwelveDataApiException(Exception):
    """Exception class for issues coming from Twelve Data API.

    Examples
    ----------
    >>> try:
    ...     raise TwelveDataApiException(500, "Erreur")
    ... except TwelveDataApiException as e:
    ...     print(e.code, e.message)
    500 Erreur

    """

    def __init__(self, code, message):
        self.code = code
        self.message = message


def handle_exception(func):
    """Wrapper for exceptions handling.

    This wrapper catch exceptions.

    Parameters
    ----------
    func : function
        Function called within the wrapper.

    Examples
    ----------
    Let's define a simple function that raise TwelveDataApiException if its argument is True :

    >>> @handle_exception
    ... def foo(raise_exception: bool):
    ...     if raise_exception:
    ...         raise TwelveDataApiException(500, "Erreur")
    ...     else:
    ...         return "Nothing hapenned"
    >>> foo(raise_exception=True)
    {'status': 'error', 'code': 500, 'message': 'Erreur'}
    >>> foo(raise_exception=False)
    'Nothing hapenned'

    Now, let's raise the exception from foo() :



    Finally, let's see what happens when no exception is raised :


    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except TwelveDataApiException as e:
            logger.error(e)
            return {"status": "error", "code": e.code, "message": e.message}

        except AssertionError as e:
            logger.error(e)
            return {"status": "error", "code": 500, "message": e.args[0]}

        except TypeCheckError as e:
            logger.error(e)
            return {"status": "error", "code": 500, "message": str(e)}

    return wrapper
