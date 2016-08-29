__author__ = 'nasim'
from rss.models import RssFeeds, BaseNews
import feedparser
import datetime
import dateutil.parser
from django.utils import timezone
from django.utils.dateparse import parse_date
import pytz
import re

def link_preprocessing(url, name):
    return url
    if name == 'asriran':
        p = re.compile(r'http:\/\/www.asriran.com\/fa\/news\/[0-9]*')
        url = p.findall(url)[0]
    return url

def get_new_rss():
# can do with thread future.Future

    for rss in RssFeeds.objects.all():
        if rss.activation==False:
            continue

        feed = feedparser.parse(rss.main_rss)
        try:
            feed_time = dateutil.parser.parse(feed['feed']['updated'])
        except:
            feed_time =max([dateutil.parser.parse(ti['published']) for ti in feed['items']])


        print(timezone.is_aware(rss.last_modified),rss.last_modified)
        feed_time = feed_time.replace(tzinfo=pytz.UTC)
        print(timezone.is_aware(feed_time),feed_time)

        if feed_time > rss.last_modified:
            last = rss.last_modified
            rss.last_modified = feed_time
            rss.save()
            for item in feed['items']:
                item_publish_time = dateutil.parser.parse(item['published'])
                if item_publish_time > last:
                    try:
                        BaseNews.objects.update_or_create(url=link_preprocessing(item['link'],rss.name),
                                                defaults={
                                                    'rss':rss,
                                                    'title':item['title'],
                                                    'published_date':item_publish_time})
                    except Exception:
                        continue
                else:
                    break
