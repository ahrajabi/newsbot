# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-14 14:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0006_entity_positive'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='min_should',
            field=models.IntegerField(default=1),
        ),
    ]
