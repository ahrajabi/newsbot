from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Entity(models.Model):
    STATUS = (
        ('N', 'New' ),
        ('P' , 'Pending'),
        ('A', 'Activated'),
        ('R' , 'Rejected'),
        ('D' , 'Deleted'),
    )

    name = models.CharField(max_length=50)
    status = models.CharField(max_length=1,default='N',choices=STATUS)
    followers = models.IntegerField(default=0)
    news_count = models.IntegerField(default=0)
    last_news = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return self.name


class UserEntity(models.Model):
    STATUS = (
        (True, 'Fallow'),
        (False , 'Unfallow'),
    )

    user = models.ForeignKey(User)
    entity = models.ForeignKey(Entity)
    status = models.BooleanField(default=True,choices=STATUS)
    score = models.SmallIntegerField(default=0)
    last_news = models.DateTimeField(null=True,blank=True)
    news_count = models.IntegerField(default=0)


    def __str__(self):
        return self.user.username + " has " + self.entity.name

