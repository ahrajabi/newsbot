# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-19 06:01
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('telegrambot', '0006_auto_20160916_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='usernewslist',
            name='datetime_start',
            field=models.DateTimeField(default=datetime.datetime(2001, 8, 15, 8, 15, 12, tzinfo=utc)),
        ),
        migrations.AddField(
            model_name='usernewslist',
            name='page',
            field=models.PositiveIntegerField(default=1, verbose_name='Page that list is'),
        ),
    ]
