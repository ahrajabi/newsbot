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
from rss.ml import normalize
from entities.management.commands.store_entities import add_or_update_entity

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

        try:
            if 'PDFIcon' in td[6].contents[1]['class']:
                pdf_link = td[6].contents[1]['href']
            else:
                pdf_link = None
        except KeyError:
            pdf_link = None

        data.append({
            "namad": normalize(td[0].text.strip()),
            "company": normalize(td[1].text.strip()),
            "title": normalize(td[2].text.strip()),
            "time": normalize(td[3].text.strip()),
            "datetime": farsidate_to_date(td[3].text.strip()),
            "link": link,
            "pdf_link": pdf_link
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
                                                                       'summary': body,
                                                                       'pdf_link': item['pdf_link'],})
            if is_created:
                obj.complete_news = True
                obj.save()

        add_or_update_entity('نماد ' + item['namad'], 'A', synonym=','.join([item['namad'] , item['company']]))
