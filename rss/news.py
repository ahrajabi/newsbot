import datetime
import random
import requests
from bs4 import BeautifulSoup as bs
from rss.ml import *
from entities.tasks import get_entity_news
from rss.models import BaseNews, News, ImageUrls, NewsLike
from django.contrib.auth.models import User


def save_news(base_news):
    # fix catch HeaderParsingError
    print(str(base_news.url))
    try:
        page = requests.get(str(base_news.url), timeout=20)
        page_soup = bs(page.text, 'html.parser')
    except Exception:
        return False

    if page_soup:
        try:
            news_bodys = page_soup.select(base_news.rss.news_agency.selector)
            news_body = ' '.join([item.text for item in news_bodys])
            news_body = normalize(news_body)
        except IndexError:
            news_body = ''

        try:
            news_summary = page_soup.select(base_news.rss.news_agency.summary_selector)[0].text
            news_summary = normalize(news_summary)
        except IndexError:
            news_summary = ''

        if news_body == '' and news_summary == '':
            return False

        news, is_created = News.objects.update_or_create(base_news=base_news,
                                                         defaults={'body': news_body,
                                                                   'pic_number': 0,
                                                                   'summary': news_summary,})

        # elastic_search_store(news_body, news_summary, news.id)

        news_images = page_soup.select(base_news.rss.news_agency.image_selector)
        cnt = 0
        for img in news_images:
            try:
                ImageUrls.objects.create(img_url=img['src'], news=news)
                cnt += 1
            except Exception:
                continue
        news.pic_number = cnt

        # fake random like count
        r = random.uniform(0, 10)
        news.like_count = random.choice([r, 0, 0, 0, 1, 2, 3])



        get_entity_news([news])
        news.save()
    return True


def set_news_like(user, news, mark='Like'):
    obj, created = NewsLike.objects.update_or_create(news=news, user=user,
                                                     defaults={'status': (mark == 'Like')})
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
