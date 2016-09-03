__author__ = 'nasim'
from rss.models import BaseNews
import feedparser
import dateutil.parser
from django.utils import timezone
import pytz
from datetime import timedelta


def repair_datetime(input_datetime, rss_name):
    input_datetime = dateutil.parser.parse(input_datetime)
    if not timezone.is_aware(input_datetime):
        input_datetime = input_datetime.replace(tzinfo=pytz.utc)

    delta = timedelta(hours=4, minutes=30)
    if rss_name in ['irna', 'fars']:
        input_datetime -= delta

    return timezone.localtime(input_datetime)


def get_new_rss(rss):
    print(rss.name)
    feed = feedparser.parse(rss.main_rss)
    try:
        feed_time = feed['feed']['updated']
    except:
        feed_time = max([ti['published'] for ti in feed['items']])

    feed_time = repair_datetime(feed_time, rss.name)

    if feed_time > rss.last_modified:
        last = rss.last_modified
        rss.last_modified = feed_time
        rss.save()
        for item in feed['items']:
            item_publish_time = repair_datetime(item['published'], rss.name)
            if item_publish_time > last:
                print(item['title'])
                BaseNews.objects.update_or_create(title=item['title'],
                                                  url=item['link'],
                                                  defaults={
                                                      'rss': rss,
                                                      'published_date': item_publish_time})
            else:
                break

