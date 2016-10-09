from celery import shared_task
from rss.rss import get_new_rss
from rss.models import RssFeeds
from rss.models import BaseNews, News
import datetime
from rss.news import save_news
from rss.elastic import source_generator, es
from elasticsearch import helpers
from django.core.cache import cache
from hashlib import md5
import random
from django.conf import settings
from rss.codal import get_new_codal
from django.utils import timezone

LOCK_EXPIRE = 60 * 2


@shared_task
def get_all_new_news():
    HOUR_NOW = timezone.localtime(timezone.now()).hour
    # Reject get news in 24:00 - 06:00

    if 0 < HOUR_NOW < 6:
        return False

    THREAD_RSS_NUM = settings.CELERY_WORKER_NUM
    all_rss = RssFeeds.objects.all()
    all_rss = [item.id for item in all_rss]

    for j in range(THREAD_RSS_NUM):
        rss_list = all_rss[j::THREAD_RSS_NUM]
        print(rss_list)
        lock_id = '{0}-lock-{1}-{2}'.format('rss', str(j), str(THREAD_RSS_NUM))
        acquire_lock = lambda: cache.add(lock_id, 'true', LOCK_EXPIRE)
        release_lock = lambda: cache.delete(lock_id)
        get_new_rss_async.delay(rss_list)

        if acquire_lock() and False:
            try:
                get_new_rss_async.delay(rss_list)
            finally:
                release_lock()

    get_new_codal()
    bulk_save_to_elastic()


@shared_task
def get_new_rss_async(rss_list):
    start_time = datetime.datetime.now()

    random.shuffle(rss_list)
    for id in rss_list:
        rss = RssFeeds.objects.get(id=id)
        print(rss.news_agency.name)
        if not rss.activation:
            continue
        get_new_rss(rss)

    print('GET NEW RSS', datetime.datetime.now() - start_time)


def save_base_news_async(id):
    obj = BaseNews.objects.get(id=id)
    if obj.complete_news:
        return
    try:
        if save_news(obj):
            obj.complete_news = True
            obj.save()
    except:
        pass


def bulk_save_to_elastic():
    start_time = datetime.datetime.now()
    sources = list()
    for obj in News.objects.filter(base_news__save_to_elastic=False)[0:500]:
        fields_keys = ('body', 'summary', 'title', 'published_date')
        fields_values = (obj.body, obj.summary, obj.base_news.title, obj.base_news.published_date)
        source = dict(zip(fields_keys, fields_values))
        sources.append((obj, source))

    k = ({'_index': settings.ELASTIC_NEWS['index'], '_type': settings.ELASTIC_NEWS['doc_type'], '_id': ret[0].id,
          "_source": ret[1]}
         for ret in sources)
    ret = helpers.bulk(es, k, chunk_size=500, max_chunk_bytes=200 * 1024 * 1024)

    if ret[0] == len(sources):
        for item in sources:
            item[0].base_news.save_to_elastic = True
            item[0].base_news.save()
    else:
        print("___ERROR IN ELASTIC BULK SAVE", ret)
    print('_ELASTIC_', datetime.datetime.now() - start_time)


@shared_task
def get_codal():
    get_new_codal()
    bulk_save_to_elastic()
