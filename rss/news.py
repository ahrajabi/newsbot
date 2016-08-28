__author__ = 'nasim'
import datetime
import requests
from bs4 import BeautifulSoup as bs

from rss.models import BaseNews, News, ImageUrls


def save_news(base_news):
    # fix catch HeaderParsingError
    try:
        print(str(base_news.url))
        page = requests.get(str(base_news.url),  timeout=20)
    except Exception:
        base_news.delete()
        return False

    page_soup = bs(page.text, 'html.parser')
    if page_soup:
        try:
            news_body = page_soup.select(base_news.rss.selector)[0].text
        except IndexError:
            news_body = ''

        try:
            news_summary = page_soup.select(base_news.rss.summary_selector)[0].text
        except IndexError:
            news_summary = ''

        news, is_created = News.objects.update_or_create(base_news=base_news,
                                             defaults={'body': news_body,
                                                       'pic_number': 0,
                                                       'summary': news_summary, })

        # elastic_search_store(news_body, news_summary, news.id)

        news_images = page_soup.select(base_news.rss.image_selector)
        cnt = 0
        for img in news_images:
            try:
                ImageUrls.objects.create(img_url=img['src'], news=news)
                cnt += 1
            except Exception:
                continue
        news.pic_number = cnt
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
