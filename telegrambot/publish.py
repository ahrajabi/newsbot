from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from telegram.error import Unauthorized
from telegram import InlineKeyboardMarkup
from telegram.inlinekeyboardbutton import InlineKeyboardButton
from rss import elastic
from rss.models import News
from entities.tasks import get_user_entity
from entities.models import UserEntity
from telegrambot import news_template, bot_send
from telegrambot.models import UserNewsList, UserProfile, UserLiveNews
from telegrambot.command_handler import deactive_profile
from telegrambot.bot_template import publish_news
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, NetworkError)


def publish_handler(bot, job):
    try:
        cache.incr('publish_handler_counter')
    except ValueError:
        cache.set('publish_handler_counter', 1)
    cnt = cache.get('publish_handler_counter')

    # if cnt * job.interval % 200 == 0:
    #     periodic_publish_news(bot, job)
    #     print('periodic', cnt)
    # else:
    #     live_publish_news(bot, job)
    print('time', cnt)
    periodic_publish_news(bot, job)


def prepare_periodic_publish_news(bot, job, up, alert_no_news=False):
    del job
    user = up.user
    interval = up.user_settings.interval_news_list

    if hasattr(up.user_settings, 'last_news_list') and up.user_settings.last_news_list:
        start_time = up.user_settings.last_news_list.datetime_publish
    else:
        ue = UserEntity.objects.filter(user=user, status=True)

        if ue.count() >= settings.REQUIRED_ENTITY:
            start_time = timezone.now() - timedelta(days=7)
        else:
            start_time = timezone.now() - timedelta(minutes=interval)

    el_news = elastic.news_with_terms(entity_list=get_user_entity(user),
                                      size=settings.NEWS_PER_PAGE,
                                      start_time=start_time)

    try:
        news_ent = [item['_id'] for item in el_news['hits']['hits']]
    except KeyError:
        print("ES DIDN'T RETURN RIGHT JSON! See publish.py")
        return False

    unl = UserNewsList.objects.create(user=user,
                                      datetime_start=start_time,
                                      datetime_publish=timezone.now(),
                                      number_of_news=el_news['hits']['total'],
                                      page=1)

    up.user_settings.last_news_list = unl
    up.user_settings.save()
    if len(news_ent) == 0:
        if alert_no_news:
            output = '👌' + 'شما تمام خبرهای مرتبط با دسته های خود را خوانده اید.'
            bot_send.send_telegram_user(bot, user, output)
    elif len(news_ent) < 4:
        for item in news_ent:
            try:
                news = News.objects.get(id=item)
                publish_news(bot, news, user)
            except News.DoesNotExist:
                pass
    else:
        news_list = news_ent
        output = 'اخبار مرتبط با نشان‌های شما'
        output += '\n'
        output += news_template.prepare_multiple_sample_news(news_list, settings.NEWS_PER_PAGE)
        keyboard = None
        if el_news['hits']['total'] > settings.NEWS_PER_PAGE:
            buttons = [[
                InlineKeyboardButton(text='صفحه بعد', callback_data='entitynewslist-next'),
            ], ]
            keyboard = InlineKeyboardMarkup(buttons)

        try:
            result = bot_send.send_telegram_user(bot, user, output, keyboard=keyboard)
            unl.message_id = result.message_id
            unl.save()
        except Unauthorized:
            deactive_profile(up)


def periodic_publish_news(bot, job):
    hour_now = timezone.localtime(timezone.now()).hour

    if 0 < hour_now < 6:
        return False

    for up in UserProfile.objects.all():
        interval = up.user_settings.interval_news_list
        delta = timezone.now() - timedelta(minutes=interval)

        if not up.activated or up.stopped or len(get_user_entity(up.user)) == 0:
            continue

        if up.user_settings.last_news_list and up.user_settings.last_news_list.datetime_publish >= delta:
            continue

        prepare_periodic_publish_news(bot, job, up)


def live_publish_news(bot, job):
    del job
    for up in UserProfile.objects.filter(user_settings__live_news=True, activated=True, stopped=False):
        news_ent = UserLiveNews.objects.filter(user=up.user, is_sent=False)

        if news_ent.count() > 0:
            for item in news_ent:
                item.is_sent = True
                item.save()

            news_list = list(set([item.news.id for item in news_ent]))
            output = 'اخبار زنده نشان‌های شما'
            output += '\n'
            output += news_template.prepare_multiple_sample_news(news_list, 20)
            try:
                bot_send.send_telegram_user(bot, up.user, output)
            except Unauthorized:
                deactive_profile(up)
