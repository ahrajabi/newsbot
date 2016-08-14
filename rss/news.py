__author__ = 'nasim'
import requests
from bs4 import BeautifulSoup as bs
from rss.models import BaseNews, News
from bs4 import BeautifulSoup as bs



def save_news(base_news):
    page = requests.get(base_news.url).text
    page_soup = bs(page, 'html.parser')
    if page_soup:
        news_body = page_soup.select(base_news.rss.selector)
        try:
            news_summary = page_soup.select(base_news.rss.summary_selector)
        except (IndexError):
            news_summary = ''
        news = News.objects.create(body=news_body, summary=news_summary)
        news.basenews_ptr = base_news



