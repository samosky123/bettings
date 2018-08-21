import datetime
import logging
from django.db import models
from django.utils import timezone

from bettings.bets.models import Bet
from .constants import ErrorResponse
from .exceptions import InvalidRequestException

logger = logging.getLogger(__name__)


# Create your models here.
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Tournament(TimestampedModel):
    name = models.CharField(max_length=128)
    start_date = models.DateField()
    end_date = models.DateField()

    def get_year(self):
        return self.start_date.year

    def __str__(self):
        return "{} - {}".format(self.name, self.get_year())


class Team(TimestampedModel):
    name = models.CharField(max_length=128)
    founded_at = models.PositiveIntegerField(default=datetime.datetime.now().year)
    symbol = models.ImageField(upload_to="team_symbols", blank=True, null=True)
    tournaments = models.ManyToManyField(Tournament, related_name="teams")

    def __str__(self):
        return self.name


def get_odds_choices() -> list:
    odds = []
    for i in range(-20, 20):
        i = i * 0.25
        odds.append((i, i))
    return odds


class Match(TimestampedModel):
    start_time = models.DateTimeField(default=timezone.now)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="matches")
    home = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches")
    guest = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="guest_matches")
    odds = models.DecimalField(max_digits=3, decimal_places=2, choices=get_odds_choices(), default=0)

    def has_result(self):
        return hasattr(self, "result") and self.result is not None

    def get_profitability_ratio(self) -> float:
        if not self.has_result():
            raise InvalidRequestException(ErrorResponse.MATCH_HAS_NO_RESULT)
        ratio = self.result.home_goals - (self.result.guest_goals + self.odds)
        logger.info("Profitability ratio of match [{}] is [{}]".format(self.pk, ratio))
        return ratio

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.pk:
            # create new match
            return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        old_match = Match.objects.get(pk=self.pk)
        if not old_match.has_result() or old_match.odds == self.odds:
            # old match does not have result yet or odds not change
            return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        # update bet result
        self.result.save()
        return

    def __str__(self):
        return "{} - {} in {}".format(self.home, self.guest, self.tournament)


class MatchResult(TimestampedModel):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name="result")
    home_goals = models.PositiveIntegerField()
    guest_goals = models.PositiveIntegerField()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        # update bet result
        logger.info("Updating all bet results of match [{}]".format(self.match.pk))
        bets = Bet.objects.filter(match=self.match)
        for bet in bets:
            bet.update_result()
        logger.info("Updated all bet results of match [{}] successfully".format(self.match.pk))
        return

    def __str__(self):
        return "{} {}-{} {}".format(self.match.home, self.home_goals, self.guest_goals, self.match.guest)
