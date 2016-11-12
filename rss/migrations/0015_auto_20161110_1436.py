# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-10 11:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rss', '0014_auto_20161018_2106'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='telegram'),
        ),
        migrations.AddField(
            model_name='news',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='telegram'),
        ),
        migrations.AlterField(
            model_name='basenews',
            name='source_type',
            field=models.IntegerField(choices=[(1, 'Website RSS'), (2, 'Codal'), (3, 'Telegram')], default=1,
                                      verbose_name='Type of source'),
        ),
    ]