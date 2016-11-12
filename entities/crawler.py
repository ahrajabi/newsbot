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


def map_namad(inp):
    maps = [
        ('شرکتهای چند رشته‌ای صنعتی', []),
        ('پیمانکاری صنعتی', []),
        ('استخراج کانه‌های فلزی', ['صنعت فلزات و معادن', ]),
        ('خودرو و ساخت قطعات', ['صنعت خودرو', ]),
        ('ماشین آلات و تجهیزات', ['صنعت خودرو', ]),
        ('مواد و محصولات دارویی', ['صنعت ابزار پزشکی و دارو', ]),
        ('محصولات چوبی', []),
        ('استخراج سایر معادن', ['صنعت فلزات و معادن', ]),
        ('استخراج زغال سنگ', ['صنعت فلزات و معادن', ]),
        ('لاستیک و پلاستیک', ['صنعت پلیمر و پلاستیک', ]),
        ('کاشی و سرامیک', ['صنعت فلزات و معادن', 'صنعت راه و ساختمان', ]),
        ('فلزات اساسی', ['صنعت فلزات و معادن', ]),
        ('زراعت و خدمات وابسته', ['صنعت غذا و کشاورزی', ]),
        ('انتشار، چاپ و تکثیر', ['صنعت چاپ', ]),
        ('سرمایه گذاریها', ['صنعت بانک و بیمه', ]),
        ('بانکها و موسسات اعتباری', ['صنعت بانک و بیمه', ]),
        ('محصولات شیمیایی', ['صنعت شیمیایی و حلال‌ها', ]),
        ('سایر محصولات کانی غیرفلزی', ['صنعت فلزات و معادن', ]),
        ('قند و شکر', ['صنعت غذا و کشاورزی', ]),
        ('ساخت محصولات فلزی', ['صنعت فلزات و معادن', ]),
        ('سایر واسطه گریهای مالی', []),
        ('ماشین آلات و دستگاه‌های برقی', []),
        ('انبوه سازی، املاک و مستغلات', ['صنعت راه و ساختمان', ]),
        ('محصولات کاغذی', ['صنعت چاپ', ]),
        ('حمل و نقل آبی', ['صنعت راه و ساختمان', ]),
        ('فراورده‌های نفتی، کک و سوخت هسته‌ای', ['صنعت نفت و گاز', ]),
        ('عرضه برق، گاز، بخاروآب گرم', []),
        ('حمل ونقل، انبارداری و ارتباطات', []),
        ('واسطه‌گری‌های مالی و پولی', ['صنعت بانک و بیمه', ]),
        ('دباغی، پرداخت چرم و ساخت انواع پاپوش', ['صنعت نساجی و پوشاک', ]),
        ('بیمه وصندوق بازنشستگی به جزتامین اجتماعی', ['صنعت بانک و بیمه', ]),
        ('فعالیتهای کمکی به نهادهای مالی واسط', ['صنعت بانک و بیمه', ]),
        ('استخراج نفت گاز و خدمات جنبی جز اکتشاف', ['صنعت نفت و گاز', 'صنعت پتروشیمی و پالایش', ]),
        ('رایانه و فعالیت‌های وابسته به آن', ['ارتباطات و فناوری اطلاعات', ]),
        ('منسوجات', ['صنعت نساجی و پوشاک', ]),
        ('ابزارپزشکی، اپتیکی و اندازه‌گیری', ['صنعت ابزار پزشکی و دارو', ]),
        ('ساخت دستگاه‌ها و وسایل ارتباطی', ['ارتباطات و فناوری اطلاعات', ]),
        ('محصولات غذایی و آشامیدنی به جز قند و شکر', ['صنعت غذا و کشاورزی', ]),
        ('خدمات فنی و مهندسی', []),
        ('سیمان، آهک و گچ', ['صنعت فلزات و معادن', 'صنعت راه و ساختمان', ]),
        ('مخابرات', ['ارتباطات و فناوری اطلاعات', ]),
    ]
    for item in maps:
        if inp == item[0]:
            return item[1]
