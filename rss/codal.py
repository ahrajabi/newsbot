import requests
from bs4 import BeautifulSoup as bs
from rss import ml
import re
import jdatetime
import datetime
import pytz
from rss.models import BaseNews, News, NewsAgency
from rss.ml import per_to_eng
from django.conf import settings
from django.utils.timezone import tzinfo
from rss.rss import repair_datetime
from entities.models import Entity

def farsidate_to_date(farsidate):
    farsidate = re.split(':|/| ', farsidate)
    date = jdatetime.JalaliToGregorian(jyear=int(per_to_eng(farsidate[0])),
                                       jmonth=int(per_to_eng(farsidate[1])),
                                       jday=int(per_to_eng(farsidate[2])))
    date = datetime.datetime(year=date.gyear,
                             month=date.gmonth,
                             day=date.gday,
                             hour=int(per_to_eng(farsidate[3])),
                             minute=int(per_to_eng(farsidate[4])),
                             second=int(per_to_eng(farsidate[5])), )

    return repair_datetime(date, True)


def get_new_codal():
    url = 'http://codal.ir'
    page = requests.get(url, timeout=20)
    page_soup = bs(page.text, 'html.parser')
    data = list()
    if not page_soup:
        return
    rows = page_soup.select('.ReportListGrid tr')
    for item in rows[1:]:
        td = item.select('td')
        link = td[2].select('a')[0]['href']
        if not link.startswith('http'):
            link = 'http://codal.ir/' + link
        data.append({
            "namad": td[0].text.strip(),
            "company": td[1].text.strip(),
            "title": td[2].text.strip(),
            "time": td[3].text.strip(),
            "datetime": farsidate_to_date(td[3].text.strip()),
            "link": link
        })
    codalagency = NewsAgency.objects.get(name='codal')

    for item in data:
        title = item['namad'] + ' - ' + item['title']
        body = item['namad'] + ' - ' + item['company'] + ' - ' + item['title']
        obj, created = BaseNews.objects.update_or_create(title=title,
                                                         url=item['link'][
                                                             0:BaseNews._meta.get_field('url').max_length - 2],
                                                         defaults={'news_agency': codalagency,
                                                                   'published_date': item['datetime'],
                                                                   'source_type': 2})

        if created:
            news, is_created = News.objects.update_or_create(base_news=obj,
                                                             defaults={'body': body,
                                                                       'pic_number': 0,
                                                                       'summary': body,})
            if is_created:
                obj.complete_news = True
                obj.save()
        if 'نماد ' + item['namad'] not in Entity.objects.filter(status='A').values_list('name', flat=True):
            company = Entity.objects.get_or_create(name=item['company'], status='R')[0]
            symbol = Entity.objects.get_or_create(name=item['namad'], status='R')[0]
            obj = Entity.objects.create(name='نماد ' + item['namad'], status='A')
            obj.related.add(company, symbol)
