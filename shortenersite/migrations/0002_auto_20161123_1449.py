# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-23 11:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('shortenersite', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='urls',
            name='httpurl',
            field=models.URLField(max_length=500),
        ),
    ]
