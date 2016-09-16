# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-15 12:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('telegrambot', '0004_auto_20160914_1237'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageFromUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_id', models.CharField(blank=True, max_length=1000, null=True)),
                ('chat_id', models.CharField(blank=True, max_length=1000, null=True)),
                ('type', models.IntegerField(choices=[(1, 'Text'), (2, 'Command'), (3, 'Callback'), (4, 'other')], default=4)),
                ('message', models.TextField()),
                ('date', models.DateTimeField(verbose_name='received date')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]