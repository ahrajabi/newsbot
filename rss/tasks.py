from celery import shared_task
from rss.rss import get_new_rss
from rss.models import RssFeeds
from rss.models import BaseNews
import datetime
from rss.news import save_news
from rss.elastic import source_generator, es
from elasticsearch import helpers
from django.core.cache import cache
from hashlib import md5
import random
from django.conf import settings
LOCK_EXPIRE = 60*2


@shared_task
def get_all_new_news():
    bulk_save_to_elastic()
    THREAD_RSS_NUM = settings.CELERY_WORKER_NUM
    all_rss = RssFeeds.objects.all()
    all_rss = [item.id for item in all_rss]

    for j in range(THREAD_RSS_NUM):
        rss_list = all_rss[j::THREAD_RSS_NUM]
        print(rss_list)
        lock_id = '{0}-lock-{1}-{2}'.format('rss', str(j), str(THREAD_RSS_NUM))
        acquire_lock = lambda: cache.add(lock_id, 'true', LOCK_EXPIRE)
        release_lock = lambda: cache.delete(lock_id)

        if acquire_lock():
            try:
                get_new_rss_async.delay(rss_list)
            finally:
                release_lock()



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


@shared_task
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


@shared_task
def bulk_save_to_elastic():
    start_time = datetime.datetime.now()
    k = ({'_index': settings.ELASTIC_NEWS, '_type': 'new', '_id': idx, "_source": source}
         for idx, source in source_generator())
    helpers.bulk(es, k)
    print('_ELASTIC_', datetime.datetime.now() - start_time)

