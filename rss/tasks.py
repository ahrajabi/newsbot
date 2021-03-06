from celery import shared_task
from rss.rss import get_new_rss
from rss.models import RssFeeds
from rss.models import BaseNews, News
import datetime
from rss.news import save_news
from rss.ml import normalize
from rss.elastic import es
from elasticsearch import helpers
from django.core.cache import cache
import random
from django.conf import settings
from rss.codal import get_new_codal
from django.utils import timezone
from rss.heterogeneous_rss import get_all_hg_news

LOCK_EXPIRE = 60 * 2


@shared_task
def get_all_new_news():
    hour_now = timezone.localtime(timezone.now()).hour
    # Reject get news in 24:00 - 06:00
    if 0 < hour_now< 6:
        return False

    thread_rss_num = settings.CELERY_WORKER_NUM - 1
    all_rss = RssFeeds.objects.filter(activation=True)
    all_rss = [item.id for item in all_rss]

    for j in range(thread_rss_num):
        rss_list = all_rss[j::thread_rss_num]
        print(rss_list)
        lock_id = '{0}-lock-{1}-{2}'.format('rss', str(j), str(thread_rss_num))
        acquire_lock = lambda: cache.add(lock_id, 'true', LOCK_EXPIRE)
        release_lock = lambda: cache.delete(lock_id)
        get_new_rss_async.delay(rss_list)

        if acquire_lock() and False:
            try:
                get_new_rss_async.delay(rss_list)
            finally:
                release_lock()

    # get_new_codal()
    get_all_hg_news()

    bulk_save_to_elastic()


@shared_task
def telegram_crawler_async():
    hour_now = timezone.localtime(timezone.now()).hour
    # Reject get news in 24:00 - 06:00
    if 0 < hour_now < 6:
        return False
    from rss import tg
    tg.telegram_crawler()


@shared_task
def get_new_rss_async(rss_list):
    start_time = datetime.datetime.now()

    random.shuffle(rss_list)
    for item in rss_list:
        rss = RssFeeds.objects.get(id=item)
        print(rss.news_agency.name)
        if not rss.activation:
            continue
        get_new_rss(rss)

    print('GET NEW RSS', datetime.datetime.now() - start_time)


def save_base_news_async(ide):
    obj = BaseNews.objects.get(id=ide)
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
        fields_values = (normalize(obj.body), normalize(obj.summary),
                         normalize(obj.base_news.title), obj.base_news.published_date)
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
