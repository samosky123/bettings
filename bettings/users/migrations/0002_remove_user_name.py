# Generated by Django 2.0.7 on 2018-07-25 09:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='name',
        ),
    ]
