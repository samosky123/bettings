from django.urls import path

from .views import BetListView, BetCreateView, BetUpdateView, BetDeleteView, BetResultView

app_name = "bets"

urlpatterns = [
    path("my-bets/", BetListView.as_view(), name="my_bets"),
    path("matches/<int:match_pk>/create/", BetCreateView.as_view(), name="create"),
    path("<int:bet_pk>/update/", BetUpdateView.as_view(), name="update"),
    path("<int:bet_pk>/delete/", BetDeleteView.as_view(), name="delete"),
    path("bet-results/", BetResultView.as_view(), name="result"),
]
