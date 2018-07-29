from .constants import ErrorResponse


class BaseCustomException(Exception):
    status_code = None
    error_code = None
    error_message = None
    is_know_exception = True

    def __init__(self, error_response: ErrorResponse):
        super().__init__(error_response.message)
        self.error_code = error_response.code
        self.error_message = error_response.message

    def to_dict(self):
        return {
            "errorCode": self.error_code,
            "errorMessage": self.error_message
        }


class InvalidRequestException(BaseCustomException):
    status_code = 400
