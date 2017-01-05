# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-16 15:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rss', '0016_auto_20161114_1421'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramPost',
            fields=[
                ('id', models.CharField(max_length=63, primary_key=True, serialize=False, verbose_name='Message ID')),
                ('channel_id', models.CharField(max_length=63, verbose_name='Peer ID')),
            ],
        ),
    ]