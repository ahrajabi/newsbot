# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-18 14:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rss', '0012_categorycode_activation'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='importance',
            field=models.FloatField(blank=True, null=True, verbose_name='Importance of News'),
        ),
    ]
