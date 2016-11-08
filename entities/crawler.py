from bs4 import BeautifulSoup as bs
import requests
import redis
from .models import Entity
from rss.ml import normalize


def tnews_entity():
    cnt = 0
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    main = requests.get('http://tnews.ir').text
    soupmain = bs(main, "html.parser")
    for link in soupmain.find_all("a", {"class": "newsLink"}):
        url = 'http://tnews.ir' + link['href']
        if r.exists('tnews#' + url):
            continue
        r.set('tnews#' + url, 'Done')
        page = requests.get(url).text
        soup = bs(page, "html.parser")
        if soup:
            for item in soup.find_all("a", {"class": "tagLink"}):
                if Entity.objects.filter(name=item.text):
                    continue
                cnt += 1
                if cnt % 50 == 0:
                    print(cnt)
                Entity.objects.create(name=item.text).save()


def namad_tsetmc():
    url = 'http://www.tsetmc.com/Loader.aspx?ParTree=111C1417'
    page = requests.get(url, timeout=20)
    page_soup = bs(page.text, 'html.parser')
    data = list()
    if not page_soup:
        return

    rows = page_soup.select('#tblToGrid tr')
    for item in rows[1:]:
        td = item.select('td')
        company = normalize(td[7].text.strip())
        group = normalize(td[2].text.strip())
        namad = normalize(td[6].text.strip())
        obj, created = Entity.objects.update_or_create(for_search=namad,
                                                       defaults={
                                                           'status': 'A',
                                                           'for_search': namad,
                                                           'summary': group,
                                                           'name': 'نماد ' + namad,
                                                       })

        gobj, gcreated = Entity.objects.update_or_create(for_search=group,
                                                         defaults={
                                                             'name': 'گروه بورسی ' + group,
                                                             'status': 'R',
                                                         })

        cobj, ccreated = Entity.objects.update_or_create(for_search=company,
                                                         defaults={
                                                             'status': 'R',
                                                             'name': company,
                                                             'summary': group,
                                                         })

        if not gobj in obj.synonym.all():
            obj.synonym.add(gobj)

        if not cobj in obj.synonym.all():
            obj.synonym.add(cobj)

        obj.save()

    return data
