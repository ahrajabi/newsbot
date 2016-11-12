from django.db import models
from django.contrib.auth.models import User
from rss.models import News


# Create your models here.


class Entity(models.Model):
    STATUS = (
        ('N', 'New'),
        ('P', 'Pending'),
        ('A', 'Activated'),
        ('R', 'Rejected'),
        ('D', 'Deleted'),
    )

    name = models.CharField(max_length=70)
    for_search = models.CharField(max_length=70)
    synonym = models.ManyToManyField("self", verbose_name='Synonym to Entity', symmetrical=False,
                                     related_name='combined+')
    negative = models.ManyToManyField("self", verbose_name='Negative to Entity', symmetrical=False,
                                      related_name='combined+')
    related = models.ManyToManyField("self", verbose_name='Related to Entity', symmetrical=False,
                                     related_name='combined+')
    wiki_name = models.CharField(max_length=70, null=True)
    status = models.CharField(max_length=1, default='N', choices=STATUS)
    followers = models.IntegerField(default=0)
    news_count = models.IntegerField(default=0)
    latest_news = models.ForeignKey(News, null=True, blank=True)
    summary = models.TextField(null=True)

    def __str__(self):
        return self.name

    def get_synonym(self):
        return [item.name for item in self.synonym.all()]

    def get_negative(self):
        return [item.name for item in self.negative.all()]

    def get_related(self):
        return [item.name for item in self.related.all()]


class UserEntity(models.Model):
    STATUS = (
        (True, 'Follow'),
        (False, 'Unfollow'),
    )

    user = models.ForeignKey(User)
    entity = models.ForeignKey(Entity)
    status = models.BooleanField(default=True, choices=STATUS)
    score = models.SmallIntegerField(default=0)
    last_news = models.DateTimeField(null=True, blank=True)
    news_count = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username + " has " + self.entity.name


class NewsEntity(models.Model):
    news = models.ForeignKey(News)
    entity = models.ForeignKey(Entity)
    score = models.SmallIntegerField(default=0)

    def __str__(self):
        return str(self.news_id) + " has " + self.entity.name
