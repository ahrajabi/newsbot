import requests
import random
import feedparser
from django.utils import timezone

from rss.ml import *
from rss.rss import repair_datetime
from rss.codal import get_new_codal
from rss.models import BaseNews, News, RssFeeds
from entities.tasks import get_entity_news, live_entity_news


def get_tsetmc(rss=RssFeeds.objects.get(news_agency__name='tsetmc')):
    feed = feedparser.parse(rss.main_rss)
    try:
        feed_time = repair_datetime(max([item['published'] for item in feed['items']]), rss.news_agency.time_delay)
    except KeyError:
        return

    if feed_time > rss.last_modified:
        last = rss.last_modified
        rss.last_modified = feed_time
        rss.save()
        for item in (feed['items']):
            try:
                publish_time = repair_datetime(item['published'], rss.news_agency.time_delay)
            except Exception:
                publish_time = timezone.localtime(timezone.now())

            if publish_time > last:
                obj, created = BaseNews.objects.get_or_create(title=item['title'],
                                                              defaults={'rss': rss,
                                                                        'news_agency': rss.news_agency,
                                                                        'published_date': publish_time, })
                if rss not in obj.all_rss.all():
                    obj.all_rss.add(rss)
                    obj.save()

                if created:
                    hg_save_base_news(obj, item['summary'], item['summary'])
            else:
                break
    else:
        pass


def hg_save_base_news(obj, body, summary, pic_number=0, file=None, pdf_link=None):
    if obj.complete_news:
        return
    try:
        if hg_save_news(obj, body, summary, pic_number, file, pdf_link):
            obj.complete_news = True
            obj.save()
    except:
        pass


def hg_save_news(base_news, body, summary, pic_number, file, pdf_link):
    news, is_created = News.objects.update_or_create(base_news=base_news,
                                                     defaults={'body': normalize(body),
                                                               'pic_number': pic_number,
                                                               'summary': normalize(summary),
                                                               'file': file,
                                                               'pdf_link': pdf_link})
    news.like_count = random.choice([0, 0, 0, 1, 2, 3])
    ent_news = get_entity_news(news)
    live_entity_news(news, ent_news)

    news.save()
    return True


def get_ifb(rss=RssFeeds.objects.get(news_agency__name='ifb')):
    feed = feedparser.parse(rss.main_rss)
    try:
        feed_time = repair_datetime(max([item['published'] for item in feed['items']]), rss.news_agency.time_delay)

    except KeyError:
        return

    if feed_time > rss.last_modified:
        last = rss.last_modified
        rss.last_modified = feed_time
        rss.save()
        for item in (feed['items']):
            try:
                publish_time = repair_datetime(item['published'], rss.news_agency.time_delay)
            except Exception:
                publish_time = timezone.localtime(timezone.now())

            if publish_time > last:
                obj, created = BaseNews.objects.get_or_create(title=item['title'],
                                                              defaults={'rss': rss,
                                                                        'news_agency': rss.news_agency,
                                                                        'published_date': publish_time, })
                if rss not in obj.all_rss.all():
                    obj.all_rss.add(rss)
                    obj.save()

                if created:
                    hg_save_base_news(obj, '', '', pdf_link=item['link'])
            else:
                break
    else:
        pass


def get_all_hg_news():
    get_new_codal()
    get_tsetmc()
    get_ifb()