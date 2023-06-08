from typeguard import TypeCheckError


class TwelveDataApiException(Exception):
    """Exception class for issues coming from Twelve Data API."""

    def __init__(self, code, message):
        self.code = code
        self.message = message


def handle_exception(func):
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
