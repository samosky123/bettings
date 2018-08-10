from django.db import models


# Create your models here.
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def get_amount_choices():
    choices = []
    for i in range(1, 6):
        amount = i * 10000
        choices.append((amount, amount))
    return choices


class Bet(TimestampedModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="bets")
    match = models.ForeignKey("tournaments.Match", on_delete=models.CASCADE, related_name="bets")
    choice = models.ForeignKey("tournaments.Team", on_delete=models.CASCADE, related_name="+")
    amount = models.DecimalField(max_digits=12, decimal_places=2, choices=get_amount_choices())

    def __str__(self):
        return "{} bet on match {}".format(self.user.username, self.match)
