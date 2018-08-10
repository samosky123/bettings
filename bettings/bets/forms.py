from django import forms
from django.db.models import Q

from bettings.tournaments.models import Team
from .models import Bet


class BetCreateForm(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ("choice", "amount",)

    def __init__(self, *args, **kwargs):
        match_pk = kwargs.pop("match_pk")
        super().__init__(*args, **kwargs)
        self.fields["choice"] = forms.ModelChoiceField(
            queryset=Team.objects.filter(Q(home_matches__pk=match_pk) | Q(guest_matches__pk=match_pk)).distinct(),
            empty_label="Please choose a team")


class BetUpdateForm(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ("choice", "amount",)

    def __init__(self, *args, **kwargs):
        bet_pk = kwargs.pop("bet_pk")
        bet = Bet.objects.get(pk=bet_pk)
        match_id = bet.match.pk
        super().__init__(*args, **kwargs)
        self.initial["amount"] = round(bet.amount)
        self.fields["choice"] = forms.ModelChoiceField(label="Choose team", queryset=Team.objects.filter(
            Q(home_matches__pk=match_id) | Q(guest_matches__pk=match_id)).distinct())
        self.initial["choice"] = bet.choice.pk
