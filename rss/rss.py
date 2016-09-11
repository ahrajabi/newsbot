__author__ = 'nasim'
from rss.models import BaseNews
import feedparser
import dateutil.parser
from django.utils import timezone
import pytz
from datetime import timedelta
from rss import tasks


def repair_datetime(input_datetime, rss_delay=False):
    try:
        input_datetime = dateutil.parser.parse(input_datetime)
    except:
        input_datetime = timezone.now()
    if not timezone.is_aware(input_datetime):
        input_datetime = input_datetime.replace(tzinfo=pytz.utc)

    delta = timedelta(hours=4, minutes=30)
    if rss_delay:
        input_datetime -= delta

    return timezone.localtime(input_datetime)


def get_new_rss(rss):
    print(rss.name, rss.category)
    feed = feedparser.parse(rss.main_rss)

    try:
        if 'updated' in feed['feed'].keys():
            feed_time = feed['feed']['updated']
        else:
            feed_time = max([ti['published'] for ti in feed['items']])
    except:
        print("Failed")
        return

    feed_time = repair_datetime(feed_time, rss.time_delay)

    if feed_time > rss.last_modified:
        last = rss.last_modified
        rss.last_modified = feed_time
        rss.save()
        for item in feed['items']:
            item_publish_time = repair_datetime(item['published'], rss.time_delay)
            if item_publish_time > last:
                obj, created = BaseNews.objects.update_or_create(title=item['title'],
                                                                 url=item['link'],
                                                                 defaults={'rss': rss,
                                                                           'published_date': item_publish_time,
                                                                           })
                if created:
                    tasks.save_base_news_async(obj.id)
            else:
                break

