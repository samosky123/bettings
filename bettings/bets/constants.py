from enum import Enum


class ErrorResponse(Enum):
    BET_EXPIRED_TIME = (1, "Bet on this match is expired")

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
