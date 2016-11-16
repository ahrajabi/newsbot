# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-14 14:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('telegrambot', '0014_auto_20161114_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersearchlist',
            name='order',
            field=models.CharField(choices=[('R', 'Relevance'), ('N', 'Newest first')], default='R', max_length=1,
                                   verbose_name='Order of result'),
        ),
    ]