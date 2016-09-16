# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-14 05:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rss', '0005_auto_20160913_1037'),
    ]

    operations = [
        migrations.AddField(
            model_name='basenews',
            name='all',
            field=models.ManyToManyField(default=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rss', to='rss.RssFeeds', verbose_name='related rss feed'), to='rss.RssFeeds', verbose_name='all rss feed'),
        ),
        migrations.AlterField(
            model_name='basenews',
            name='rss',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rss', to='rss.RssFeeds', verbose_name='related rss feed'),
        ),
    ]
