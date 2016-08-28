# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-24 07:54
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BaseNews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(blank=True, max_length=600, verbose_name='News url')),
                ('title', models.TextField(blank=True, null=True, verbose_name='Tittle')),
                ('published_date', models.DateTimeField(blank=True, null=True, verbose_name='Published date ')),
                ('complete_news', models.BooleanField(default=False, verbose_name='Has full news')),
            ],
        ),
        migrations.CreateModel(
            name='CategoryCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='site Name')),
                ('fa_name', models.CharField(max_length=50, verbose_name='Persian Name')),
            ],
        ),
        migrations.CreateModel(
            name='ImageUrls',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img_url', models.URLField(max_length=500, verbose_name='image url')),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(blank=True, null=True, verbose_name='News')),
                ('summary', models.TextField(blank=True, null=True, verbose_name='summary')),
                ('pic_number', models.PositiveSmallIntegerField(verbose_name='Number of Pictures')),
                ('base_news', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rss.BaseNews', verbose_name='Related base news')),
            ],
        ),
        migrations.CreateModel(
            name='RssFeeds',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=600, verbose_name='Web site')),
                ('name', models.CharField(blank=True, max_length=200, verbose_name='site Name')),
                ('fa_name', models.CharField(blank=True, max_length=200, verbose_name='Persian Name')),
                ('category', models.CharField(blank=True, max_length=50, verbose_name='Category')),
                ('activation', models.BooleanField(default=True, verbose_name='Activation')),
                ('order', models.CharField(blank=True, choices=[('D', 'Date'), ('V', 'Visit')], max_length=50, verbose_name='RSS Order')),
                ('main_rss', models.URLField(blank=True, max_length=300, verbose_name='Web site RSS')),
                ('selector', models.CharField(blank=True, max_length=1000)),
                ('summary_selector', models.CharField(blank=True, max_length=300)),
                ('image_selector', models.CharField(blank=True, max_length=300)),
                ('last_modified', models.DateTimeField(blank=True, default=datetime.datetime(2001, 8, 15, 8, 15, 12, tzinfo=utc))),
                ('category_ref', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rss.CategoryCode')),
            ],
        ),
        migrations.AddField(
            model_name='imageurls',
            name='news',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rss.News', verbose_name='related news'),
        ),
        migrations.AddField(
            model_name='basenews',
            name='rss',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rss.RssFeeds', verbose_name='related rss feed'),
        ),
    ]
