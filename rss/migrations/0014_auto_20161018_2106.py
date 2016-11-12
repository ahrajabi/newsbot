# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-18 17:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rss', '0013_news_importance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='importance',
            field=models.FloatField(default=0, verbose_name='Importance of News'),
        ),
    ]