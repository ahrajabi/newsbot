# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-30 09:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('telegrambot', '0017_userprofile_private'),
    ]

    operations = [
        migrations.AddField(
            model_name='channelpublish',
            name='send_channel',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='channelpublish',
            name='send_codal',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='channelpublish',
            name='send_news_agency',
            field=models.BooleanField(default=False),
        ),
    ]