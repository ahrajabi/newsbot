import requests
import random
import feedparser
from django.utils import timezone

from rss.rss import repair_datetime
from rss.models import BaseNews, News
from entities.tasks import get_entity_news, live_entity_news


def get_tsetmc(rss):
    # rss = 'http://www.tsetmc.com/tsev2/feed/TseMsg.aspx?type=RSS'
    feed = feedparser.parse(rss)
    try:
        feed_time = repair_datetime(feed['items'][0]['published'], rss.news_agency.time_delay)
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
                                                                        'published_date': publish_time,})
                if not rss in obj.all_rss.all():
                    obj.all_rss.add(rss)
                    obj.save()

                if created:
                    tsetmc_save_base_news(obj, item['summary'])
            else:
                break


def tsetmc_save_base_news(obj, news):
    if obj.complete_news:
        return
    try:
        if tsetmc_save_news(obj, news):
            obj.complete_news = True
            obj.save()
    except:
        pass


def tsetmc_save_news(base_news, news):
    news, is_created = News.objects.update_or_create(base_news=base_news,
                                                     defaults={'body': news,
                                                               'pic_number': 0,
                                                               'summary': news,})
    news.like_count = random.choice([0, 0, 0, 1, 2, 3])
    ent_news = get_entity_news(news)
    live_entity_news(news, ent_news)

    news.save()