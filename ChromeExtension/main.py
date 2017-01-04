from django.utils import timezone
from shortenersite.views import shorten
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import serializers
import datetime

from entities.models import Entity
from rss.elastic import news_with_terms
from rss.models import News, TelegramPost
from entities.tasks import get_user_entity
from newsbot.settings import NEWS_PER_PAGE
from telegrambot.news_template import news_image_page


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def chrome_extension_response(request, username):
    return Response(get_user_news(username))


def get_user_news(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        # raise ValueError(u'invalid user')
        return 0

    el_news = news_with_terms(entity_list=get_user_entity(user),
                              size=NEWS_PER_PAGE,
                              start_time='now-10d',
                              sort='published_date')
    try:
        news_ent = [item['_id'] for item in el_news['hits']['hits']]
    except KeyError:
        # raise ValueError('invalid news')
        return 0

    response = []
    for news_id in news_ent:
        try:
            news = News.objects.get(id=news_id)
        except News.DoesNotExist:
            continue
        if news.base_news.source_type == 3:
            link = ""
        else:
            link = shorten(news.base_news.url)
        news = {'id': news.id,
                'summary': news.summary,
                'title': news.base_news.title,
                'published_date': timezone.localtime(news.base_news.published_date),
                'link': link,
                'agency': news.base_news.news_agency.fa_name,
                'image_link': news_image_page(news),
                }
        response.append(news)
    return response


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_telegram_codal(request):
    return Response(get_one_tg('کدال'))


def get_one_tg(name):
    posts = News.objects.filter(base_news__news_agency__fa_name=name,
                                base_news__source_type=3,
                                base_news__published_date__gte=timezone.now() - datetime.timedelta(days=10)).order_by(
        '-base_news__published_date')[:50]
    response = []
    for post in posts:
        response.append(news_serializer(post))
    return response


def news_serializer(news):
    return ({'title': news.base_news.title,
             'news': news.body,
             'photo': news_image_page(news),
             'pdf_link': news.pdf_link,
             'resource': news.base_news.news_agency.fa_name,
             'published date': news.base_news.published_date
             })


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_telegram_with_entity(request):
    '''
    sample body :
    {
    "entities":[
        "نماد وساپا"
        ]
    }
    '''
    entities = Entity.objects.filter(name__in=request.data['entities'])
    el_news = news_with_terms(entity_list=entities,
                              size=50,
                              start_time='now-10d')
    try:
        news_id = [item['_id'] for item in el_news['hits']['hits']]
    except KeyError:
        print("Elastic Didn't return Response... !")
        return False
    news = News.objects.filter(id__in=news_id, base_news__source_type=3)
    response = []
    for n in news:
        response.append(news_serializer(n))
    print('finished')
    return Response(response)

