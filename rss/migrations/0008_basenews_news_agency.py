# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-14 06:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rss', '0007_auto_20160914_1047'),
    ]

    operations = [
        migrations.AddField(
            model_name='basenews',
            name='news_agency',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='rss.NewsAgency', verbose_name='News Agency'),
            preserve_default=False,
        ),
    ]
