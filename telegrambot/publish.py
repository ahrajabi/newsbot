from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from entities.models import NewsEntity
from entities.tasks import get_user_entity
from telegrambot.models import UserNewsList, UserProfile
from telegrambot import news_template, bot_send
from django.core.cache import cache


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

    for up in UserProfile.objects.all():
        user = up.user
        interval = up.user_settings.interval_news_list
        delta = timezone.now() - timedelta(minutes=interval)
        if up.user_settings.last_news_list and up.user_settings.last_news_list.datetime_publish >= delta:
            continue
        ent = get_user_entity(user)
        news_ent = NewsEntity.objects.filter(entity__in=ent,
                                             news__base_news__published_date__range=(delta, timezone.now())) \
            .order_by('news__base_news__published_date')
        unl = UserNewsList.objects.create(user=user,
                                          datetime_publish=timezone.now(),
                                          number_of_news=news_ent.count(), )

        up.user_settings.last_news_list = unl
        up.user_settings.save()
        print(":|")
        if news_ent.count() > 0:
            news_list = list(set([item.news_id for item in news_ent]))
            output = 'اخبار مرتبط با دسته‌های شما'
            output += '\n'
            output += news_template.prepare_multiple_sample_news(news_list, 20)[0]

            bot_send.send_telegram_user(bot, user, output)


def live_publish_news(bot, job):
    if not cache.get('last_live_publish'):
        cache.set('last_live_publish', timezone.now())
    start = cache.get('last_live_publish')
    end = timezone.now()
    cache.set('last_live_publish', timezone.now())

    for up in UserProfile.objects.filter(user_settings__live_news=True):
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

            bot_send.send_telegram_user(bot, user, output)
