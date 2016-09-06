from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
import pytz


class CategoryCode(models.Model):
    name = models.CharField('site Name', max_length=50)
    fa_name = models.CharField('Persian Name', max_length=50)

    def __str__(self):
        return self.fa_name


class RssFeeds(models.Model):
    RSS_ORDER = (
        ('D', 'Date'),
        ('V', 'Visit'),
        ('F', 'Front'),
    )

    url = models.URLField('Web site', max_length=600,  blank=False)
    name = models.CharField('site Name', max_length=200, blank=True)
    fa_name = models.CharField('Persian Name', max_length=200, blank=True)
    category = models.CharField('Category', max_length=50, blank=True)
    activation = models.BooleanField('Activation', default=True)
    category_ref = models.ForeignKey(CategoryCode, blank=True, null=True)
    order = models.CharField('RSS Order', max_length=50, blank=True, choices=RSS_ORDER)
    main_rss = models.URLField('Web site RSS', max_length=300, blank=True)
    selector = models.CharField(max_length=1000, blank=True)
    summary_selector = models.CharField(max_length=300, blank=True)
    image_selector = models.CharField(max_length=300, blank=True)
    last_modified = models.DateTimeField(blank=True, default=datetime(2001, 8, 15, 8, 15, 12, 0, pytz.UTC))

    def __str__(self):
        return self.fa_name


class BaseNews(models.Model):
    url = models.URLField('News url', max_length=600, blank=True)
    rss = models.ForeignKey(RssFeeds, verbose_name='related rss feed', null=True, blank=True)
    title = models.TextField('Tittle', blank=True, null=True)
    published_date = models.DateTimeField('Published date ', blank=True, null=True)
    complete_news = models.BooleanField('Has full news', default=False)
    save_to_elastic = models.BooleanField('Saved to Elastic', default=False)

    def __str__(self):
        return self.url


class News(models.Model):
    body = models.TextField('News', blank=True, null=True)
    summary = models.TextField('summary', blank=True, null=True)
    base_news = models.OneToOneField(BaseNews, verbose_name='Related base news', null=True, blank=True)
    pic_number = models.PositiveSmallIntegerField('Number of Pictures')
    like_count = models.PositiveIntegerField('Number of Likes', default=0)


class ImageUrls(models.Model):
    img_url = models.URLField('image url', max_length=500)
    news = models.ForeignKey(News, verbose_name='related news')


class NewsLike(models.Model):
    STATUS = (
        (True, 'Like'),
        (False, 'Unlike'),
    )

    news = models.ForeignKey(News)
    user = models.ForeignKey(User)
    status = models.BooleanField(default=True, choices=STATUS)

