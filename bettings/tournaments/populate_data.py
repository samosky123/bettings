import os
import sys

root_path = os.path.join(os.path.dirname(__file__), "../..")
sys.path.append(os.path.abspath(root_path))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
#
import django

django.setup()

from django.utils import timezone
from bettings.tournaments.models import Tournament, Team, Match

from faker import Faker

fakegen = Faker()
import random
import datetime


def get_odds():
    odds = []
    for i in range(-20, 20):
        i = i * 0.25
        odds.append(i)
    return odds


def generate_data(num_tour=10, num_team=20, num_match=380):
    print("Generating fake data...")
    start_date = datetime.date(2018, 1, 17)
    end_date = datetime.date(2019, 1, 17)
    tournament = Tournament.objects.create(name="Test Tournament", start_date=start_date, end_date=end_date)
    for i in range(0, num_tour):
        start_date = fakegen.date_of_birth()
        end_date = fakegen.date_between_dates(date_start=start_date)
        Tournament.objects.create(name=fakegen.name(), start_date=start_date, end_date=end_date)
    teams = []
    for i in range(0, num_team):
        team = Team.objects.create(name=fakegen.name(), founded_at=fakegen.year())
        team.tournaments.add(tournament)
        teams.append(team)
    for i in range(0, num_match):
        start_date_time = datetime.datetime.combine(start_date, datetime.datetime.min.time())
        end_date_time = datetime.datetime.combine(end_date, datetime.datetime.min.time())
        chosen_teams = random.sample(teams, 2)
        home = chosen_teams[0]
        guest = chosen_teams[1]
        Match.objects.create(
            start_time=timezone.make_aware(fakegen.date_time_between_dates(datetime_start=start_date_time, datetime_end=end_date_time)),
            tournament=tournament, home=home, guest=guest, odds=random.choice(get_odds()))
    print("Finished generate data")


if __name__ == "__main__":
    generate_data(num_tour=0)
