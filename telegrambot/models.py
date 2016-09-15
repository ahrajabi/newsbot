from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from rss.models import News


class UserProfile(models.Model):
    user = models.ForeignKey(User)
    first_name = models.CharField(max_length=140)
    last_name = models.CharField(max_length=140)
    last_chat = models.DateTimeField()
    telegram_id = models.PositiveIntegerField()

    def __unicode__(self):
        return u'Profile of user: %s' % self.user.username


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
