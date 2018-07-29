from django.urls import path

from .views import TournamentListView, MatchListView

app_name = "tournaments"
urlpatterns = [
    path("", TournamentListView.as_view(), name="list"),
    path("<int:tournament_pk>/", MatchListView.as_view(), name="match_list"),
]
