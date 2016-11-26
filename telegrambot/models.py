from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from rss.models import News, CategoryCode
import pytz
from datetime import datetime


class UserNewsList(models.Model):
    user = models.ForeignKey(User, verbose_name='User')
    datetime_start = models.DateTimeField(default=datetime(2001, 8, 15, 8, 15, 12, 0, pytz.UTC))
    datetime_publish = models.DateTimeField(default=datetime(2001, 8, 15, 8, 15, 12, 0, pytz.UTC))
    number_of_news = models.PositiveIntegerField(verbose_name='Number of News of list')
    message_id = models.PositiveIntegerField(verbose_name="Message ID", null=True)
    page = models.PositiveIntegerField(verbose_name="Page that list is", default=1)


class UserSearchList(models.Model):
    ORDER = (
        ('R', 'Relevance'),
        ('N', 'Newest first'),
    )
    user = models.ForeignKey(User, verbose_name='User')
    query = models.TextField()
    datetime_start = models.DateTimeField(default=datetime(2001, 8, 15, 8, 15, 12, 0, pytz.UTC))
    datetime_publish = models.DateTimeField(default=datetime(2001, 8, 15, 8, 15, 12, 0, pytz.UTC))
    number_of_news = models.PositiveIntegerField(verbose_name='Number of News of list')
    message_id = models.PositiveIntegerField(verbose_name="Message ID", null=True)
    page = models.PositiveIntegerField(verbose_name="Page that list is", default=1)
    order = models.CharField(max_length=1, verbose_name='Order of result', default='R', choices=ORDER)


class UserSettings(models.Model):
    live_news = models.BooleanField(default=False)
    interval_news_list = models.PositiveSmallIntegerField(default=120)
    last_news_list = models.OneToOneField(UserNewsList, verbose_name='Last News List', null=True)


class UserProfile(models.Model):
    user = models.ForeignKey(User)
    activated = models.BooleanField(verbose_name='Bot Blocked', default=True)
    stopped = models.BooleanField(verbose_name='Bot Stopped', default=False)
    private = models.BooleanField(verbose_name='Private', default=False)
    first_name = models.CharField(max_length=140, null=True)
    last_name = models.CharField(max_length=140, null=True)
    last_chat = models.DateTimeField()
    telegram_id = models.PositiveIntegerField()
    user_settings = models.OneToOneField(UserSettings, verbose_name='User Settings', null=True)
    interest_categories = models.ManyToManyField(CategoryCode, verbose_name="Interest user categories", blank=True)

    def __unicode__(self):
        return u'Profile of user: %s' % self.user.username

    def toggle_interest_categories(self, cat):
        print("HELLOss")
        if cat in self.interest_categories.all():
            self.interest_categories.remove(cat)
            for item in cat.get_children():
                if item in self.interest_categories.all():
                    self.interest_categories.remove(item)
        else:
            self.interest_categories.add(cat)


class UserAlert(models.Model):
    text = models.TextField(null=True)
    send_time = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)


class UserNews(models.Model):
    user = models.ForeignKey(User)
    news = models.ForeignKey(News)
    page = models.PositiveIntegerField(default=0)
    image_page = models.PositiveIntegerField(default=0)


class MessageFromUser(models.Model):
    MESSAGE_TYPE = (
        (1, 'Text'),
        (2, 'Command'),
        (3, 'Callback'),
        (4, 'other')
    )
    user = models.ForeignKey(User)
    message_id = models.CharField(null=True, blank=True, max_length=1000)
    chat_id = models.CharField(null=True, blank=True, max_length=1000)
    type = models.IntegerField(choices=MESSAGE_TYPE, default=4)
    message = models.TextField()
    date = models.DateTimeField(verbose_name='received date')

    def save(self, *args, **kwargs):
        self.date = timezone.now()
        return super(MessageFromUser, self).save(*args, **kwargs)


class UserLiveNews(models.Model):
    user = models.ForeignKey(User)
    news = models.ForeignKey(News)
    is_sent = models.BooleanField(default=False)


class ChannelPublish(models.Model):
    channel_username = models.CharField(max_length=120)
    last_news = models.PositiveIntegerField(default=0)
