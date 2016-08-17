from django.db import models
from django.contrib.auth.models import User

# Create your models here.


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
    send_time = models.DateTimeField(null=True,blank=True)
    is_sent = models.BooleanField(default=False)
