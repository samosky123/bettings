import datetime
import logging

from django.db.models import Case, When, Value, BooleanField
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import ListView

from .forms import TournamentSearchForm, MatchSearchForm
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
        context["search_form"] = TournamentSearchForm()
        return context

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        name = request.GET.get("name")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        content = "Get all tournaments"
        if name:
            content += "by name contains [{}]".format(name)
            queryset = queryset.filter(name__contains=name)
        if start_date:
            try:
                date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                content += ", by start date after [{}]".format(start_date)
                queryset = queryset.filter(start_date__gte=date)
            except ValueError:
                logger.error("Cannot parse start date [{}] by format [%Y-%m-%d]".format(start_date))
        if end_date:
            try:
                date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                content += ", by end date before [{}]".format(end_date)
                queryset = queryset.filter(end_date__lte=date)
            except ValueError:
                logger.error("Cannot parse end date [{}] by format [%Y-%m-%d]".format(end_date))
        logger.info(content)
        self.object_list = queryset
        allow_empty = self.get_allow_empty()
        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
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
        context["search_form"] = MatchSearchForm()
        return context

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        start_time = request.GET.get("start_time")
        if start_time:
            time = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
            logger.info("Search start time of match after [{}]".format(time))
            queryset = queryset.filter(start_time__gte=timezone.make_aware(time))
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
