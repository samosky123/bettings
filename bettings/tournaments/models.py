import datetime

from django.db import models
from django.utils import timezone


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

    def __str__(self):
        return "{} - {} in {}".format(self.home, self.guest, self.tournament)

    def has_result(self):
        return hasattr(self, "result") and self.result is not None


class MatchResult(TimestampedModel):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name="result")
    home_goals = models.PositiveIntegerField()
    guest_goals = models.PositiveIntegerField()

    def __str__(self):
        return "{} {}-{} {}".format(self.match.home, self.home_goals, self.guest_goals, self.match.guest)
