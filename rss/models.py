from django.db import models
from datetime import datetime
import pytz

class RssFeeds(models.Model):
    url = models.URLField('Web site', max_length=600,  blank=False)
    name = models.CharField('site Name', max_length=200, blank=True)
    fa_name = models.CharField('Persian Name', max_length=200, blank=True)
    main_rss = models.URLField('Web site RSS', max_length=300, blank=True)
    selector = models.CharField(max_length=1000, blank=True)
    last_modified = models.DateTimeField(blank=True, default=datetime(2001, 8, 15, 8, 15, 12, 0, pytz.UTC))
    summary_selector = models.CharField(max_length=300, blank=True)
    image_selector = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return self.fa_name

class BaseNews(models.Model):
    url = models.URLField('News url',max_length=600, blank=True)
    rss = models.ForeignKey(RssFeeds, verbose_name='related rss feed', null=True, blank=True)
    title = models.TextField('Tittle', blank=True, null=True)
    published_date = models.DateTimeField('Published date ', blank=True, null=True)
    complete_news = models.BooleanField('Has full news', default=False)

    def __str__(self):
        return self.url

class News(models.Model):
    body = models.TextField('News', blank=True, null=True)
    summary = models.TextField('summary', blank=True, null=True)
    base_news = models.OneToOneField(BaseNews, verbose_name='Related base news', null=True, blank=True)
    pic_number = models.PositiveSmallIntegerField('Number of Pictures')


class ImageUrls(models.Model):
    img_url = models.URLField('image url', max_length=500)
    news = models.ForeignKey(News, verbose_name='related news')