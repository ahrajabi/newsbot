from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    user = models.ForeignKey(User)
    first_name = models.CharField(max_length=140)
    last_name = models.CharField(max_length=140)
    last_chat = models.DateTimeField()

    def __unicode__(self):
        return u'Profile of user: %s' % self.user.username