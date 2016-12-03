from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
import pytz
from rss import ml
from mptt.models import MPTTModel, TreeForeignKey


class NewsAgency(models.Model):
    url = models.URLField('Web site', max_length=50)
    name = models.CharField('site Name', max_length=50)
    fa_name = models.CharField('Persian Name', max_length=50)
    selector = models.CharField(max_length=100, blank=True)
    summary_selector = models.CharField(max_length=100, blank=True)
    image_selector = models.CharField(max_length=100, blank=True)
    time_delay = models.BooleanField('Time Delay', default=False)

    def __str__(self):
        return self.name


class CategoryCode(MPTTModel):
    name = models.CharField('site Name', max_length=50)
    fa_name = models.CharField('Persian Name', max_length=50)
    activation = models.BooleanField('Activation', default=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.fa_name


class RssFeeds(models.Model):
    RSS_ORDER = (
        ('D', 'Date'),
        ('V', 'Visit'),
        ('F', 'Front'),
        ('VF', 'Visit in frontpage'),
    )

    news_agency = models.ForeignKey(NewsAgency)
    category = models.CharField('Category', max_length=50, blank=True)
    activation = models.BooleanField('Activation', default=True)
    category_ref = models.ForeignKey(CategoryCode, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.CharField('RSS Order', max_length=50, blank=True, choices=RSS_ORDER)
    main_rss = models.URLField('Web site RSS', max_length=300, blank=True)
    last_modified = models.DateTimeField(blank=True, default=datetime(2001, 8, 15, 8, 15, 12, 0, pytz.UTC))

    def __str__(self):
        return self.news_agency.fa_name + " " + self.category


class BaseNews(models.Model):
    SOURCE = (
        (1, 'Website RSS'),
        (2, 'Codal'),
        (3, 'Telegram')
    )

    url = models.URLField('News url', max_length=600, blank=True)
    rss = models.ForeignKey(RssFeeds, verbose_name='related rss feed', null=True, blank=True, related_name='rss')
    news_agency = models.ForeignKey(NewsAgency, verbose_name='News Agency')
    source_type = models.IntegerField(verbose_name='Type of source', default=1, choices=SOURCE)
    all_rss = models.ManyToManyField(RssFeeds, verbose_name='all rss feed', default=rss)
    title = models.TextField('Tittle', blank=True, null=True)
    published_date = models.DateTimeField('Published date ', blank=True, null=True)
    complete_news = models.BooleanField('Has full news', default=False)
    save_to_elastic = models.BooleanField('Saved to Elastic', default=False)

    def __str__(self):
        return self.url


class News(models.Model):
    importance = models.FloatField('Importance of News', default=0)
    body = models.TextField('News', blank=True, null=True)
    summary = models.TextField('summary', blank=True, null=True)
    base_news = models.OneToOneField(BaseNews, verbose_name='Related base news', null=True, blank=True)
    pic_number = models.PositiveSmallIntegerField('Number of Pictures')
    like_count = models.PositiveIntegerField('Number of Likes', default=0)
    unlike_count = models.PositiveIntegerField('Number of Un-Likes', default=0)
    photo = models.ImageField(upload_to='telegram/%Y/%m/%d/', null=True, blank=True)
    file = models.FileField(upload_to='telegram/%Y/%m/%d/', null=True, blank=True)
    pdf_link = models.URLField('pdf link', max_length=600, null=True, blank=True)

    def get_summary(self):
        if len(self.summary) > 5:
            text = self.summary
        elif len(self.body) > 5:
            text = self.body[0:300]
        else:
            text = self.base_news.title
        return ' '.join(ml.sent_tokenize(text, num_char=300))


class ImageUrls(models.Model):
    img_url = models.URLField('image url', max_length=500)
    news = models.ForeignKey(News, verbose_name='related news')


class NewsLike(models.Model):
    STATUS = (
        ('L', 'Like'),
        ('U', 'Unlike'),
        ('D', 'Discard'),
    )

    news = models.ForeignKey(News)
    user = models.ForeignKey(User)
    vote = models.CharField(default='D', max_length=1, choices=STATUS)


class TelegramPost(models.Model):
    id = models.CharField(max_length=63, verbose_name="Message ID", primary_key=True)
    channel_id = models.CharField(max_length=63, verbose_name='Peer ID')
    news = models.OneToOneField(News, verbose_name='News', null=True, blank=True)
    reply_to = models.ForeignKey('self', verbose_name='Replied to', null=True, blank=True)


class BadNews(News):
    pass