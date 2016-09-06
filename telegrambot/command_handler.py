import sys
from telegram.emoji import Emoji
from django.utils import timezone
from django.contrib.auth.models import User


from entities import tasks
from rss.models import News
from entities.models import Entity
from telegrambot import bot_template
from entities.tasks import get_entity_text
from newsbot.settings import GLOBAL_SETTINGS
from rss.elastic import elastic_search_entity
from telegrambot.models import UserAlert, UserProfile
from telegrambot.bot_template import show_related_entities
from telegrambot.news_template import prepare_multiple_sample_news
from telegrambot.bot_send import send_telegram, error_text, send_telegram_all_user
thismodule = sys.modules[__name__]


def handle(bot, msg, user):
    # TODO set len hits
    search_box_result(bot, msg, user)


def verify_user(bot, msg):
    new_user = 0
    user = get_user(msg.message.from_user.id)
    if not user:
        new_user = 1
        user = create_new_user_profile(bot, msg)
    return user, new_user


def create_new_user_profile(bot, msg):
    user = User.objects.create_user(username=msg.message.from_user.username)
    user.userprofile_set.create(first_name=msg.message.from_user.first_name,
                                last_name=msg.message.from_user.last_name,
                                last_chat=timezone.now(),
                                telegram_id=msg.message.from_user.id,
                                )
    return user


def get_user(telegram_id):
    profiles = UserProfile.objects.filter(telegram_id=telegram_id)
    if not profiles:
        return False
    user = [i.user for i in profiles][0]
    if not user:
        return None
    return user


def add_command(bot, msg, user):
    entity_id = int(msg.message.text[5:])
    entity = tasks.get_entity(entity_id)
    if entity in tasks.get_user_entity(user):
        error_text(bot, msg, type='PriorFollow')
        return
    if tasks.set_entity(user, entity_id, 1):
        bot_template.change_entity(bot, msg, entity, type=1)
        entity.followers += 1
        entity.save()
    else:
        error_text(bot, msg)


def remove_command(bot, msg, user):
    entity_id = int(msg.message.text[8:])
    entity = tasks.get_entity(entity_id)
    if entity not in tasks.get_user_entity(user):
        error_text(bot, msg, type='NoFallow')
        return

    if tasks.set_entity(user, entity_id, 0):
        bot_template.change_entity(bot, msg, entity, type=0)
        entity.followers -= 1
        entity.save()
    else:
        error_text(bot, msg)


def list_command(bot, msg, user):
    bot_template.show_user_entity(bot, msg, user, tasks.get_user_entity(user))


def help_command(bot, msg, user):
    bot_template.bot_help(bot, msg, user)


def user_alert_handler(bot, job):
    bulk = UserAlert.objects.filter(is_sent=False)
    for item in bulk:
        send_telegram_all_user(bot, item.text)
        item.is_sent = True
        item.save()


def start_command(bot, msg, new_user):
    if new_user:
        bot_template.welcome_text(bot, msg)
    else:
        error_text(bot, msg, type="RepetitiveStart")


def news_command(bot, msg, user):
    news_id = command_separator(msg, 'add')
    try:
        news = News.objects.get(id=news_id)
        bot_template.publish_news(bot, news, user, page=1, message_id=None)
    except News.DoesNotExist:
        return error_text(bot, msg, 'NoneNews')


def command_separator(msg, command):
    return int(msg.message.text[len(command)+3:])


def search_box_result(bot, msg, user):
    text = msg.message.text
    hits = elastic_search_entity(text)
    related_entities = get_entity_text(text)
    response = "%s خبرهای مرتبط:\n" % Emoji.NEWSPAPER
    response_len = 0
    news_id = []

    if hits:
        m_response, m_response_len = prepare_multiple_sample_news(list(map(int, [hit['_id'] for hit in hits])),
                                                              GLOBAL_SETTINGS['SAMPLE_NEWS_COUNT'])
        response += m_response
        response_len += m_response_len

        for index in hits[:GLOBAL_SETTINGS['SAMPLE_NEWS_COUNT']]:
            news_id.append(index['_id'])

    if response_len < GLOBAL_SETTINGS['SAMPLE_NEWS_COUNT']:
        for entity in related_entities:
            related_hits = elastic_search_entity(entity.name)
            for hit in related_hits:
                if response_len >= GLOBAL_SETTINGS['SAMPLE_NEWS_COUNT']:
                    break
                elif hit['_id'] not in news_id:
                    news_id.append(hit['_id'])
                    r_response, r_response_len = prepare_multiple_sample_news([int(hit['_id'])], 1)
                    response += r_response
                    response_len += r_response_len

    try:
        entity = Entity.objects.get(name=text)
        if entity not in related_entities:
            related_entities.insert(0, entity)
    except Entity.DoesNotExist:
        if len(hits) >= GLOBAL_SETTINGS['MIN_HITS_ENTITY_VALIDATION']:
            new_entity = Entity.objects.create(name=text, wiki_name="")
            related_entities.insert(0, new_entity)

    if not related_entities:
        error_text(bot, msg, 'InvalidEntity')
        return

    else:
        e_response = show_related_entities(related_entities)

    final_response = response + '\n' + e_response
    send_telegram(bot, msg, final_response)
