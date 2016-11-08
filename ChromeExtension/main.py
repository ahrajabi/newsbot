from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from rss.models import News
from rss.elastic import news_with_terms
from entities.tasks import get_user_entity
from newsbot.settings import NEWS_PER_PAGE
from django.utils import timezone
from shortenersite.views import shorten


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

    ent = get_user_entity(user)
    el_news = news_with_terms(terms_list=[item.name for item in ent],
                              size=NEWS_PER_PAGE,
                              start_time='now-120m',
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

        news = {'id': news.id,
                'summary': news.summary,
                'title': news.base_news.title,
                'published_date': timezone.localtime(news.base_news.published_date),
                'link': shorten(news.base_news.url),
                'agency': news.base_news.news_agency.fa_name
                }
        response.append(news)
    return response
