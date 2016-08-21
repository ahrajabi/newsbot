__author__ = 'nasim'
import datetime
import requests
import elasticsearch
from django.db import DataError
from bs4 import BeautifulSoup as bs
from requests.exceptions import ConnectionError

from rss.models import BaseNews, News, ImageUrls

es = elasticsearch. Elasticsearch(['http://130.185.76.171:9200'])


def save_news(base_news):
    # fix catch HeaderParsingError
    try:
        page = requests.get(base_news.url,  timeout=20).text
    except ConnectionError:
        print('error')
        return False

    page_soup = bs(page, 'html.parser')
    if page_soup:

        try:
            news_body = page_soup.select(base_news.rss.selector)[0].text
        except IndexError:
            news_body = ''

        try:
            news_summary = page_soup.select(base_news.rss.summary_selector)[0].text
        except IndexError:
            news_summary = ''

        news = News.objects.create(body=news_body, summary=news_summary, base_news=base_news)
        # elastic_search_store(news_body, news_summary, news.id)

        news_images = page_soup.select(base_news.rss.selector + ' img')
        for img in news_images:
            try:
                ImageUrls.objects.create(img_url=img['src'], news=news)
            except DataError:
                continue
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


def save_to_elastic_search(news_body, news_summary, news_id):

    body = {
        'news_body': news_body,
        'news_summary': news_summary,
    }
    es.index(index='news', doc_type='new', id=news_id, body=body, request_timeout=20)


def postgres_news_to_elastic(obj):
    start_time = datetime.datetime.now()
    save_to_elastic_search(obj.body, obj.summary, obj.id)
    print(datetime.datetime.now() - start_time)
