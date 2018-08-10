import datetime
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, When, Value, BooleanField
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from bettings.tournaments.models import Match
from .constants import ErrorResponse
from .exceptions import InvalidRequestException
from .forms import BetCreateForm, BetUpdateForm
from .models import Bet

# Create your views here.
logger = logging.getLogger(__name__)


class BetListView(LoginRequiredMixin, ListView):
    model = Bet
    context_object_name = 'bets'
    template_name = "bets/bet_list.html"
    paginate_by = 10

    def get_queryset(self):
        logger.info("Getting all bet of user [{}]".format(self.request.user.pk))
        modify_time = timezone.now() + datetime.timedelta(minutes=30)
        queryset = Bet.objects.filter(user=self.request.user).annotate(
            can_modify=Case(When(match__start_time__gte=modify_time, match__result=None, then=Value(True)),
                            default=Value(False),
                            output_field=BooleanField()))
        return queryset.order_by("-modified_at")


class BetCreateView(LoginRequiredMixin, CreateView):
    model = Bet
    form_class = BetCreateForm
    template_name = "bets/bet_create.html"

    def get(self, request, *args, **kwargs):
        self.match = get_object_or_404(Match, pk=self.kwargs.get("match_pk"))
        last_bet_time = self.match.start_time - datetime.timedelta(minutes=30)
        if timezone.now() >= last_bet_time or self.match.has_result():
            logger.error("User [{}] can not bet on match [{}] due to expired time".format(self.request.user.pk, self.match.pk))
            raise InvalidRequestException(ErrorResponse.BET_EXPIRED_TIME)
        bet = Bet.objects.filter(match=self.match, user=self.request.user)
        if bet:
            return HttpResponseRedirect(reverse_lazy("bets:update", kwargs={"bet_pk": bet[0].pk}))
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(self.kwargs)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["match"] = self.match
        context["tournament"] = self.match.tournament
        return context

    def get_success_url(self):
        return reverse_lazy("bets:my_bets")

    def form_valid(self, form):
        match = get_object_or_404(Match, pk=self.kwargs.get("match_pk"))
        last_bet_time = match.start_time - datetime.timedelta(minutes=30)
        user = self.request.user
        if timezone.now() >= last_bet_time or match.has_result():
            logger.error("User [{}] can not bet on match [{}] due to expired time".format(user.pk, match.pk))
            raise InvalidRequestException(ErrorResponse.BET_EXPIRED_TIME)
        bet = form.save(commit=False)
        bet.match = match
        bet.user = user
        bet.save()
        logger.info("User [{}] created bet [{}] at match [{}] with choice [{}] and amount [{}] successfully"
                    .format(self.request.user.pk, bet.pk, match.pk, bet.choice, bet.amount))
        return HttpResponseRedirect(self.get_success_url())


class BetUpdateView(LoginRequiredMixin, UpdateView):
    model = Bet
    form_class = BetUpdateForm
    pk_url_kwarg = "bet_pk"
    context_object_name = "bet"
    template_name = "bets/bet_update.html"

    def get(self, request, *args, **kwargs):
        self.bet = get_object_or_404(Bet, pk=self.kwargs.get("bet_pk"))
        match = self.bet.match
        last_bet_time = match.start_time - datetime.timedelta(minutes=30)
        if timezone.now() >= last_bet_time or match.has_result():
            logger.error("User [{}] can not bet on match [{}] due to expired time".format(self.request.user.pk, match.pk))
            raise InvalidRequestException(ErrorResponse.BET_EXPIRED_TIME)
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(self.kwargs)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["match"] = self.bet.match
        context["tournament"] = self.bet.match.tournament
        return context

    def get_success_url(self):
        return reverse_lazy("bets:my_bets")

    def form_valid(self, form):
        bet = get_object_or_404(Bet, pk=self.kwargs.get("bet_pk"))
        last_bet_time = bet.match.start_time - datetime.timedelta(minutes=30)
        user = self.request.user
        if timezone.make_aware(datetime.datetime.now()) >= last_bet_time or bet.match.has_result():
            logger.error("User [{}] can not update bet [{}] due to expired time".format(user.pk, bet.pk))
            raise InvalidRequestException(ErrorResponse.BET_EXPIRED_TIME)
        bet = form.save(commit=True)
        logger.info("User [{}] updated bet [{}] on match [{}] with choice [{}] and amount [{}] successfully"
                    .format(user.pk, bet.pk, bet.match.pk, bet.choice, bet.amount))
        return HttpResponseRedirect(self.get_success_url())


class BetDeleteView(LoginRequiredMixin, DeleteView):
    model = Bet
    pk_url_kwarg = "bet_pk"
    context_object_name = "bet"
    template_name = "bets/bet_confirm_delete.html"

    def get(self, request, *args, **kwargs):
        self.bet = get_object_or_404(Bet, pk=self.kwargs.get("bet_pk"))
        match = self.bet.match
        last_bet_time = match.start_time - datetime.timedelta(minutes=30)
        if timezone.now() >= last_bet_time or match.has_result():
            logger.error("User [{}] can not delete bet [{}] due to expired time".format(self.request.user.pk, self.bet.pk))
            raise InvalidRequestException(ErrorResponse.BET_EXPIRED_TIME)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["match"] = self.bet.match
        context["tournament"] = self.bet.match.tournament
        return context

    def get_success_url(self):
        return reverse_lazy("bets:my_bets")

    def post(self, request, *args, **kwargs):
        bet = get_object_or_404(Bet, pk=self.kwargs.get("bet_pk"))
        match = bet.match
        last_bet_time = match.start_time - datetime.timedelta(minutes=30)
        if timezone.now() >= last_bet_time or match.has_result():
            logger.error("User [{}] can not delete bet [{}] due to expired time".format(self.request.user.pk, bet.pk))
            raise InvalidRequestException(ErrorResponse.BET_EXPIRED_TIME)
        logger.info("User [{}] deleted bet [{}] successfully".format(self.request.user.pk, bet.pk))
        return self.delete(request, *args, **kwargs)
