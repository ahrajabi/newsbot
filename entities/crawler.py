from bs4 import BeautifulSoup as bs
import requests
import redis
from .models import Entity


def tnews_entity():
    cnt = 0
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    main = requests.get('http://tnews.ir').text
    soupmain = bs(main , "html.parser")
    for link in soupmain.find_all("a" , {"class":"newsLink"}):
        url = 'http://tnews.ir'+link['href']
        if r.exists('tnews#'+url):
            continue
        r.set('tnews#'+url,'Done')
        page = requests.get(url).text
        soup = bs(page , "html.parser")
        if soup :
            for item in soup.find_all("a" , {"class":"tagLink"} ):
                if Entity.objects.filter(name=item.text):
                    continue
                cnt+=1
                if cnt %50 ==0:
                    print(cnt)
                Entity.objects.create(name=item.text).save()



