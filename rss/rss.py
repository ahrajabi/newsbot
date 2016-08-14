__author__ = 'nasim'
from rss.models import RssFeeds, BaseNews
import feedparser
import datetime
import dateutil.parser

def get_new_rss():
# can do with thread future.Future
    for rss in RssFeeds.objects.all():
        feed = feedparser.parse(rss.main_rss)
        try:
            feed_time = dateutil.parser.parse(feed['feed']['updated'])
            if feed_time > rss.last_modified:
                for item in feed['items']:
                    item_publish_time = dateutil.parser.parse(item['published'])
                    if item_publish_time > rss.last_modified:
                        BaseNews.objects.create(rss=rss, url=item['link'],
                                                title=item['title'], published_date=item_publish_time)
                    else:
                        break
            rss.last_modified = feed_time
            rss.save()
        except KeyError:
            print(item)
        except TimeoutError:
            pass


