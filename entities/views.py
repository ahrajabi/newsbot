from django.shortcuts import render
from entities.models import Entity
from rss.elastic import news_with_terms
from rss.models import News
# Create your views here.


def symbols(request):
    en = Entity.objects.filter(status='A')
    return render(request, "symbols.html", {'items': en})


def symbols_id(request, entity_id):
    en = Entity.objects.get(status='A', id=entity_id)
    en_news = news_with_terms(entity_list=[en],
                              size=100,
                              start_time='now-100d',
                              sort='published_date')
    try:
        news_ent = [item['_id'] for item in en_news['hits']['hits']]
    except KeyError:
        # raise ValueError('invalid news')
        return 0

    response = []
    for news_id in news_ent:
        try:
            news = News.objects.get(id=news_id)
        except News.DoesNotExist:
            continue

        response.append(news)

    return render(request, "symbols-id.html", {'items': response})
