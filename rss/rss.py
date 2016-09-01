__author__ = 'nasim'
from rss.models import RssFeeds, BaseNews
import feedparser
import dateutil.parser
from django.utils import timezone
import pytz
from datetime import timedelta

def repair_datetime(input_datetime):
    input_datetime = dateutil.parser.parse(input_datetime)
    if not timezone.is_aware(input_datetime):
        input_datetime = input_datetime.replace(tzinfo=pytz.UTC)
    delta = timedelta(hours=4, minutes=30)
    if input_datetime - timezone.now() > delta - timedelta(hours=1):
        input_datetime -= delta
    return input_datetime

def get_new_rss():
# can do with thread future.Future
    for rss in RssFeeds.objects.all():
        print(rss.name)
        if not rss.activation:
            continue
        feed = feedparser.parse(rss.main_rss)
        try:
            feed_time = feed['feed']['updated']
        except:
            feed_time = max([ti['published'] for ti in feed['items']])

        feed_time = repair_datetime(feed_time)

        if feed_time > rss.last_modified:
            last = rss.last_modified
            rss.last_modified = feed_time
            rss.save()
            for item in feed['items']:
                item_publish_time = repair_datetime(item['published'])
                if item_publish_time > last:
                    BaseNews.objects.update_or_create(title=item['title'],
                                                      url=item['link'],
                                                      defaults={
                                                          'rss': rss,
                                                          'published_date': item_publish_time})
                else:
                    break

