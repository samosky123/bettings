import datetime
import logging

from django import forms
from django.utils import timezone

from .constants import ErrorResponse
from .exceptions import InvalidRequestException
from .models import Tournament, Match

logger = logging.getLogger(__name__)


class TournamentCreateForm(forms.ModelForm):
    def is_valid(self):
        tournament = self.save(commit=False)
        if tournament.start_date > tournament.end_date:
            logger.error("Create tournament with start date after end date")
            raise InvalidRequestException(ErrorResponse.TOURNAMENT_START_DATE_AFTER_END_DATE)
        tournament.save()
        return True

    class Meta:
        model = Tournament
        fields = "__all__"


class MatchCreateForm(forms.ModelForm):
    def is_valid(self):
        match = self.save(commit=False)
        tournament = match.tournament
        tournament_start_time = datetime.datetime.combine(tournament.start_date, datetime.datetime.min.time())
        tournament_end_time = datetime.datetime.combine(tournament.end_date, datetime.datetime.min.time())
        start_time_aware = timezone.make_aware(tournament_start_time)
        end_time_aware = timezone.make_aware(tournament_end_time)
        if match.start_time < start_time_aware:
            logger.error("Create match with start time before start date of tournament")
            raise InvalidRequestException(ErrorResponse.MATCH_START_TIME_BEFORE_START_DATE)
        elif match.start_time > end_time_aware:
            logger.error("Create match with start time after end date of tournament")
            raise InvalidRequestException(ErrorResponse.TOURNAMENT_START_DATE_AFTER_END_DATE)
        if match.home == match.guest:
            logger.error("Create match with only one team")
            raise InvalidRequestException(ErrorResponse.MATCH_HAVE_ONLY_ONE_TEAM)
        if tournament not in list(match.home.tournaments.all()) or tournament not in list(match.guest.tournaments.all()):
            logger.error("Create match with team is not in the tournament")
            raise InvalidRequestException(ErrorResponse.MATCH_TEAM_TOURNAMENT_NOT_MATCH)
        match.save()
        logger.info("Create a new match successfully")
        return True

    class Meta:
        model = Match
        fields = "__all__"


class TournamentSearchForm(forms.Form):
    name = forms.CharField(required=False)
    start_date = forms.DateField(required=False, widget=forms.TextInput(attrs={"type": "date"}))
    end_date = forms.DateField(required=False, widget=forms.TextInput(attrs={"type": "date"}))


class MatchSearchForm(forms.Form):
    start_time = forms.DateTimeField(required=False, widget=forms.TextInput(attrs={"type": "datetime-local"}))
