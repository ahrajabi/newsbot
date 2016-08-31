__author__ = 'nasim'
import datetime
import requests
from bs4 import BeautifulSoup as bs
from entities.tasks import get_entity_news
from rss.models import BaseNews, News, ImageUrls, NewsLike
from rss.ml import *
import random

def save_news(base_news):
    # fix catch HeaderParsingError
    try:
        print(str(base_news.url))
        page = requests.get(str(base_news.url),  timeout=20)
    except Exception:
        return False

    page_soup = bs(page.text, 'html.parser')
    if page_soup:
        try:
            news_bodys = page_soup.select(base_news.rss.selector)
            news_body = ' '.join([item.text for item in news_bodys])
            news_body = normalize(news_body)
        except IndexError:
            news_body = ''
            return False

        try:
            news_summary = page_soup.select(base_news.rss.summary_selector)[0].text
            news_summary = normalize(news_summary)
        except IndexError:
            news_summary = ''

        news, is_created = News.objects.update_or_create(base_news=base_news,
                                             defaults={'body': news_body,
                                                       'pic_number': 0,
                                                       'summary': news_summary, })

        #elastic_search_store(news_body, news_summary, news.id)

        news_images = page_soup.select(base_news.rss.image_selector)
        cnt = 0
        for img in news_images:
            try:
                ImageUrls.objects.create(img_url=img['src'], news=news)
                cnt += 1
            except Exception:
                continue
        news.pic_number = cnt

        #fake random like count
        r = random.uniform(0,20)
        news.like_count = random.choice([r, 0, 0, 0, 1, 2, 3])

        get_entity_news([news])
        news.save()
    return True


def save_all_base_news():
    """ for each base news with complete_news = False , get all news and create related News object """
    print("starting ... ")
    now = datetime.datetime.now()
    for obj in BaseNews.objects.filter(complete_news=False):
        print(obj.id)
        if save_news(obj):
            obj.complete_news = True
            obj.save()
        else:
            continue
    print(datetime.datetime.now() - now)


def set_news_like(user, news, mark='Like'):
    obj, created = NewsLike.objects.update_or_create(news=news, user=user,
                                                     defaults={'status': (mark=='Like')})
    if mark == 'Like':
        news.like_count += 1
    elif mark == 'Unlike':
        if news.like_count > 0:
            news.like_count -= 1
    news.save()

    return obj


def is_liked_news(user, news):
     newslike = NewsLike.objects.filter(news=news, user=user)
     if newslike:
         return newslike[0].status
     else:
         return False
