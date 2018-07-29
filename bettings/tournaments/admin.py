from django.contrib import admin

from .forms import TournamentCreateForm, MatchCreateForm
from .models import Tournament, Team, Match, MatchResult

# Register your models here.
admin.site.register(Team)
admin.site.register(MatchResult)


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    exclude = []
    form = TournamentCreateForm


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    exclude = []
    form = MatchCreateForm
