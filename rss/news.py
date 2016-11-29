import datetime
import random
import requests
from bs4 import BeautifulSoup as bs
from rss.ml import *
from entities.tasks import get_entity_news, live_entity_news
from rss.models import BaseNews, News, ImageUrls, NewsLike
from django.contrib.auth.models import User
from urllib.parse import urljoin, urlsplit
from rss.elastic import highlights_news


def save_news(base_news):
    # fix catch HeaderParsingError
    print(str(base_news.url))
    page = requests.get(str(base_news.url), timeout=20)
    if page.encoding is not 'utf-8':
        page.encoding='utf-8'
    page_soup = bs(page.text, 'html.parser')

    if page_soup:
        base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(base_news.url))

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

        if base_news.rss.news_agency.name == 'tse':
            try:
                pdf_link = page_soup.select('ul#relFiles a')[0]
                if hasattr(pdf_link, 'href'):
                    pdf_link = base_news.rss.news_agency.url + pdf_link['href']
                else:
                    pdf_link = None
            except IndexError:
                pdf_link = None
        else:
            pdf_link = None
        news, is_created = News.objects.update_or_create(base_news=base_news,
                                                         defaults={'body': news_body,
                                                                   'pic_number': 0,
                                                                   'summary': news_summary,
                                                                   'pdf_link': pdf_link,})

        news_images = page_soup.select(base_news.rss.news_agency.image_selector)
        cnt = 0
        for img in news_images:
            try:
                imglink = img['src']
                if not imglink.startswith('http'):
                    imglink = urljoin(base_url, imglink)
                ImageUrls.objects.create(img_url=imglink, news=news)
                cnt += 1
            except Exception:
                continue
        news.pic_number = cnt

        # fake random like count
        news.like_count = random.choice([0, 0, 0, 1, 2, 3])

        # if news_summary != '':
        #     highlights_news(query=news_summary)
        # else:
        #     highlights_news(query=base_news.title)
        ent_news = get_entity_news(news)
        live_entity_news(news, ent_news)

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
