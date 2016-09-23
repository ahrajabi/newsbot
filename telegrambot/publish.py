from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from entities.models import NewsEntity
from entities.tasks import get_user_entity
from telegrambot.models import UserNewsList, UserProfile
from telegrambot import news_template, bot_send, command_handler
from django.core.cache import cache
from rss import elastic
from django.conf import settings
from telegram.inlinekeyboardbutton import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.error import Unauthorized

def publish_handler(bot, job):
    try:
        cache.incr('publish_handler_counter')
    except Exception:
        cache.set('publish_handler_counter', 1)
    cnt = cache.get('publish_handler_counter')

    if cnt*job.interval % 30 == 0:
        periodic_publish_news(bot, job)
        print('periodic', cnt)
    else:
        live_publish_news(bot, job)
        print('live', cnt)


def periodic_publish_news(bot, job):
    HOUR_NOW = timezone.localtime(timezone.now()).hour
    # Reject publish news in 24:00 - 06:00

    if HOUR_NOW > 0 and HOUR_NOW < 6 :
        return False

    for up in UserProfile.objects.all().order_by('?'):
        user = up.user
        interval = up.user_settings.interval_news_list
        delta = timezone.now() - timedelta(minutes=interval)

        if up.user_settings.last_news_list and up.user_settings.last_news_list.datetime_publish >= delta:
            continue

        ent = get_user_entity(user)

        if up.user_settings.last_news_list:
            start_time = up.user_settings.last_news_list.datetime_publish
        else:
            start_time = delta

        el_news = elastic.news_with_terms(terms_list=[item.name for item in ent],
                                          size=settings.NEWS_PER_PAGE,
                                          start_time=start_time)


        try:
            news_ent = [item['_id'] for item in el_news['hits']['hits']]
        except Exception:
            print("ES DIDNT RETURN RIGHT JSON! See publish.py")
            return False

        unl = UserNewsList.objects.create(user=user,
                                          datetime_start=up.user_settings.last_news_list.datetime_publish,
                                          datetime_publish=timezone.now(),
                                          number_of_news=el_news['hits']['total'],
                                          page=1
                                          )

        up.user_settings.last_news_list = unl
        up.user_settings.save()
        if len(news_ent) > 0:
            news_list = list(set([item for item in news_ent]))
            output = 'اخبار مرتبط با دسته‌های شما'
            output += '\n'
            output += news_template.prepare_multiple_sample_news(news_list, settings.NEWS_PER_PAGE)[0]
            keyboard = None
            if el_news['hits']['total'] > settings.NEWS_PER_PAGE:
                buttons = [[
                    InlineKeyboardButton(text='صفحه بعد', callback_data='entitynewslist-next'),
                ], ]
                keyboard = InlineKeyboardMarkup(buttons)

            try:
                result = bot_send.send_telegram_user(bot, user, output, keyboard=keyboard)
            except Unauthorized:
                command_handler.deactive_profile(up)

            unl.message_id = result.message_id
            unl.save()


def live_publish_news(bot, job):
    if not cache.get('last_live_publish'):
        cache.set('last_live_publish', timezone.now())
    start = cache.get('last_live_publish')
    end = timezone.now()
    cache.set('last_live_publish', timezone.now())

    for up in UserProfile.objects.filter(user_settings__live_news=True, activated=True):
        user = up.user
        ent = get_user_entity(user)
        news_ent = NewsEntity.objects.filter(entity__in=ent,
                                             news__base_news__published_date__range=(start, end))

        news_ent2 = NewsEntity.objects.filter(news__base_news__published_date__range=(start, end))
        print(news_ent2.count())

        print(user.username, news_ent.count())
        if news_ent.count() > 0:
            news_list = list(set([item.news_id for item in news_ent]))
            output = 'اخبار زنده دسته‌های شما'
            output += '\n'
            output += news_template.prepare_multiple_sample_news(news_list, 20)[0]
            try:
                bot_send.send_telegram_user(bot, user, output)
            except Unauthorized:
                command_handler.deactive_profile(up)

