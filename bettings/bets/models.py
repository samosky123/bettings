import logging
from decimal import Decimal
from django.db import models

logger = logging.getLogger(__name__)


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
    result = models.DecimalField(max_digits=12, decimal_places=2, null=True)

    def update_result(self):
        if not self.match.has_result():
            return
        ratio = self.match.get_profitability_ratio()
        profit = self.__calculate_result(ratio)
        logger.info("Result of bet [{}] is [{}]".format(self.pk, profit))
        self.result = profit
        self.user.balance += profit
        self.save()
        self.user.save()

    def __calculate_result(self, ratio: Decimal) -> Decimal:
        if ratio >= 0.5:
            if self.choice == self.match.home:
                return self.amount
            else:
                return 0 - self.amount
        elif ratio == 0.25:
            if self.choice == self.match.home:
                return Decimal(0.5) * self.amount
            else:
                return 0 - Decimal(0.5) * self.amount
        elif ratio == 0:
            return Decimal(0)
        elif ratio == -0.25:
            if self.choice == self.match.home:
                return 0 - Decimal(0.5) * self.amount
            else:
                return 0.5 * self.amount
        else:
            if self.choice == self.match.home:
                return 0 - self.amount
            else:
                return self.amount

    def __str__(self):
        return "{} bet on match {}".format(self.user.username, self.match)
