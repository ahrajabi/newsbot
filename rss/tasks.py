from celery import task
from rss.rss import get_new_rss
from rss.models import RssFeeds
from rss.models import BaseNews, News, ImageUrls, NewsLike
import datetime
from rss.news import save_news


@task
def get_all_new_news():
    for rss in RssFeeds.objects.all():
        if not rss.activation:
            continue
        get_rss.delay(rss)


@task
def get_rss(rss):
    get_new_rss(rss)


@task
def save_all_base_news():
    """ for each base news with complete_news = False , get all news and create related News object """
    print("starting ... ")
    now = datetime.datetime.now()
    for obj in BaseNews.objects.filter(complete_news=False):
        print(obj.id)
        if save_news(obj):
            obj.complete_news = True
            obj.save()
        else:
            continue
    print(datetime.datetime.now() - now)

from rss.elastic import source_generator, es
from elasticsearch import helpers

@task
def bulk_save_to_elastic():
    start_time = datetime.datetime.now()
    k = ({'_index': 'news', '_type': 'new', '_id': idx, "_source": source}
         for idx, source in source_generator())
    helpers.bulk(es, k)
    print(datetime.datetime.now() - start_time)
