from django.db import models
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup as bs


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

    def save_news(self):
        page = requests.get(self.url).text
        page_soup = bs(page, 'html.parser')
        if page_soup:
            news_body = page_soup.select(self.rss.selector)
            try:
                news_summary = page_soup.select(self.rss.summary_selector)
            except (IndexError):
                news_summary = ''
            news = News.objects.create(body=news_body, summary=news_summary)
            news.baseactivity_ptr = self



class News(BaseNews):
    body = models.TextField('News', blank=True, null=True)
    summary = models.TextField('summary', blank=True, null=True)
    #
    # def save(self, *args, **kwargs):
    #     return super(News, self).save(*args, **kwargs)



class ImageUrls(models.Model):
    img_url = models.URLField('image url')
    news = models.ForeignKey(News, verbose_name='related news')

