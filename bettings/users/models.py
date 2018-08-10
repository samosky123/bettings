from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
