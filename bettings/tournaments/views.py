import datetime
import logging
from django.db.models import Case, When, Value, BooleanField
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils import timezone
from django.views.generic import ListView

from .models import Tournament, Match

logger = logging.getLogger(__name__)


# Create your views here.
class TournamentListView(ListView):
    model = Tournament
    template_name = "tournaments/tournament_list.html"
    context_object_name = "tournaments"
    paginate_by = 10

    def get_queryset(self):
        return Tournament.objects.all().order_by("-start_date")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name"] = self.name
        context["start_date"] = self.start_date
        context["end_date"] = self.end_date
        return context

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        self.name = request.GET.get("name")
        self.start_date = request.GET.get("start_date")
        self.end_date = request.GET.get("end_date")
        log_search = "Get all tournaments"
        if self.name:
            log_search += ", by name contains [{}]".format(self.name)
            queryset = queryset.filter(name__contains=self.name)
        if self.start_date:
            try:
                date = datetime.datetime.strptime(self.start_date, "%Y-%m-%d")
                log_search += ", by start date after [{}]".format(self.start_date)
                queryset = queryset.filter(start_date__gte=date)
            except ValueError:
                logger.error("Cannot parse start date [{}] by format [%Y-%m-%d]".format(self.start_date))
                return redirect(reverse("tournaments:list"))
        if self.end_date:
            try:
                date = datetime.datetime.strptime(self.end_date, "%Y-%m-%d")
                log_search += ", by end date before [{}]".format(self.end_date)
                queryset = queryset.filter(end_date__lte=date)
            except ValueError:
                logger.error("Cannot parse end date [{}] by format [%Y-%m-%d]".format(self.end_date))
                return redirect(reverse("tournaments:list"))
        logger.info(log_search)
        self.object_list = queryset
        allow_empty = self.get_allow_empty()
        if not allow_empty:
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                    'class_name': self.__class__.__name__,
                })
        context = self.get_context_data()
        return self.render_to_response(context)


class MatchListView(ListView):
    model = Match
    template_name = "tournaments/match_list.html"
    context_object_name = "matches"
    paginate_by = 20

    def get_queryset(self):
        tournament = get_object_or_404(Tournament, pk=self.kwargs.get("tournament_pk"))
        last_bet_time = timezone.make_aware(datetime.datetime.now() + datetime.timedelta(minutes=30))
        matches = tournament.matches.filter(tournament=tournament).annotate(
            can_bet=Case(When(start_time__gte=last_bet_time, result=None, then=Value(True)),
                         default=Value(False),
                         output_field=BooleanField()))
        return matches.order_by("start_time")

    def get_context_data(self, *, object_list=None, **kwargs):
        tournament = get_object_or_404(Tournament, pk=self.kwargs.get("tournament_pk"))
        context = super().get_context_data(**kwargs)
        context["tournament"] = tournament
        context["start_date"] = self.filter_start_date
        context["end_date"] = self.filter_end_date
        context["teams"] = list(tournament.teams.all())
        if self.filter_team_id:
            context["team_id"] = int(self.filter_team_id)
        return context

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        self.filter_start_date = request.GET.get("start_date")
        self.filter_end_date = request.GET.get("end_date")
        self.filter_team_id = request.GET.get("team_id")
        log_search = "Get all match"
        if self.filter_start_date:
            try:
                time = datetime.datetime.strptime(self.filter_start_date, "%Y-%m-%d")
            except ValueError:
                logger.error("Cannot parse start date string [{}] with format [%Y-%m-%d]".format(self.filter_start_date))
                return redirect(reverse("tournaments:match_list", kwargs={"tournament_pk": self.kwargs.get("tournament_pk")}))
            log_search += ", by start date after [{}]".format(time)
            queryset = queryset.filter(start_time__gte=timezone.make_aware(time))
        if self.filter_end_date:
            try:
                time = datetime.datetime.strptime(self.filter_end_date, "%Y-%m-%d")
            except ValueError:
                logger.error("Cannot parse end date string [{}] with format [%Y-%m-%d]".format(self.filter_end_date))
                return redirect(reverse("tournaments:match_list", kwargs={"tournament_pk": self.kwargs.get("tournament_pk")}))
            log_search += ", by end date before [{}]".format(time)
            queryset = queryset.filter(start_time__lte=timezone.make_aware(time))
        if self.filter_team_id:
            log_search += ", has team_id is [{}]".format(self.filter_team_id)
            queryset = queryset.filter(Q(home__pk=self.filter_team_id) | Q(guest__pk=self.filter_team_id))
        logger.info(log_search)
        self.object_list = queryset
        allow_empty = self.get_allow_empty()
        if not allow_empty:
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                    'class_name': self.__class__.__name__,
                })
        context = self.get_context_data()
        return self.render_to_response(context)
