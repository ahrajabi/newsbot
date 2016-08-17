__author__ = 'nasim'
import datetime
import requests
from django.db import DataError
from bs4 import BeautifulSoup as bs
from requests.packages.urllib3.exceptions import HeaderParsingError

from rss.models import BaseNews, News, ImageUrls


def save_news(base_news):
    # fix catch HeaderParsingError
    try:
        page = requests.get(base_news.url).text
    except HeaderParsingError:
        return False

    page_soup = bs(page, 'html.parser')
    if page_soup:
        news_body = page_soup.select(base_news.rss.selector)
        try:
            news_summary = page_soup.select(base_news.rss.summary_selector)
        except IndexError:
            news_summary = ''
        news = News.objects.create(body=news_body, summary=news_summary, base_news=base_news)

        news_images = page_soup.select(base_news.rss.selector + ' img')
        for img in news_images:
            try:
                ImageUrls.objects.create(img_url=img['src'], news=news)
            except DataError:
                continue
    return True


def save_all_base_news():
    """ for each base news with complete_news = False , get all news and create related News object """
    now = datetime.datetime.now()
    for obj in BaseNews.objects.filter(complete_news=False):
        if save_news(obj):
            obj.complete_news = True
            obj.save()
        else:
            continue
    print(datetime.datetime.now() - now)
