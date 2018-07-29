from enum import Enum


class ErrorResponse(Enum):
    TOURNAMENT_START_DATE_AFTER_END_DATE = (1, "Start date cannot after end date")
    MATCH_START_TIME_BEFORE_START_DATE = (2, "Start time of match cannot before start date of tournament")
    MATCH_START_TIME_AFTER_END_DATE = (3, "Start time of match cannot after end date of tournament")
    MATCH_HAVE_ONLY_ONE_TEAM = (4, "One match cannot be created by only one team")
    MATCH_TEAM_TOURNAMENT_NOT_MATCH = (5, "Tournament of match is not in the list tournaments of 2 teams")

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
