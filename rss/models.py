from django.db import models
from datetime import datetime


class RssFeeds(models.Model):
    url = models.URLField('Web site', max_length=200,  blank=False)
    name = models.CharField('site Name', max_length=200, blank=True)
    fa_name = models.CharField('Persian Name', max_length=200, blank=True)
    main_rss = models.URLField('Web site RSS', max_length=300, blank=True)
    selector = models.CharField(max_length=1000, blank=True)
    last_modified = models.DateTimeField(blank=True, default=datetime(1900, 1, 1,))
    summary_selector = models.CharField(max_length=300, blank=True)


class BaseNews(models.Model):
    url = models.URLField('News url', blank=True)
    rss = models.ForeignKey(RssFeeds, verbose_name='related rss feed', null=True, blank=True)
    title = models.TextField('Tittle', blank=True, null=True)
    published_date = models.DateTimeField('Published date ', blank=True, null=True)
    complete_news = models.BooleanField('Has full news', default=False)


class News(models.Model):
    body = models.TextField('News', blank=True, null=True)
    summary = models.TextField('summary', blank=True, null=True)
    base_news = models.OneToOneField(BaseNews, verbose_name='Related base news', null=True, blank=True)


class ImageUrls(models.Model):
    img_url = models.URLField('image url', max_length=500)
    news = models.ForeignKey(News, verbose_name='related news')
