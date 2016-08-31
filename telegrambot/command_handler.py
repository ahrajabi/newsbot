import sys
from django.utils import timezone
from django.contrib.auth.models import User

from entities import tasks
from rss.models import News
from .models import UserProfile
from telegrambot import bot_template
from telegrambot.models import UserAlert
from entities.tasks import get_entity_text
from rss.elastic import elastic_search_entity
from entities.models import Entity, UserEntity

thismodule = sys.modules[__name__]


def handle(bot, msg, user):
    text = msg.message.text
    hits = elastic_search_entity(text)
    bot_template.publish_sample_news(bot, user, msg, list(map(int, [hit['_id'] for hit in hits[:3]])))

    try:
        entity = Entity.objects.get(name=text)

    except Entity.DoesNotExist:

        related_entities = get_entity_text(text)
        # TODO set len hits
        if len(hits) < 2:
                if not related_entities:
                    bot_template.error_text(bot, msg, 'InvalidEntity')
                    return
        else:
            entity = Entity.objects.create(name=text, wiki_name="")
            related_entities.append(entity)

        bot_template.show_related_entities(bot, msg, user, related_entities)
        return

    if entity in tasks.get_user_entity(user):
        bot_template.error_text(bot, msg, type='PriorFollow')
    else:
        user_entity = UserEntity.objects.update_or_create(entity=entity, user=user)
        user_entity[0].status = True
        user_entity[0].save()
        entity.followers += 1
        entity.save()

        bot_template.after_user_add_entity(bot, msg, user, entity, tasks.get_user_entity(user))


def create_new_user_profile(bot, msg):
    user = User.objects.create_user(username=msg.message.from_user.username)
    user.userprofile_set.create(first_name=msg.message.from_user.first_name,
                                last_name=msg.message.from_user.last_name,
                                last_chat=timezone.now(),
                                telegram_id=msg.message.from_user.id,
                                )
    return user


def verify_user(bot, msg):
    new_user = 0
    user = get_user(msg.message.from_user.id)
    if not user:
        new_user = 1
        user = create_new_user_profile(bot, msg)
    return user, new_user


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
        bot_template.error_text(bot, msg, type='PriorFollow')
        return
    if tasks.set_entity(user, entity_id, 1):
        bot_template.change_entity(bot, msg, entity, type=1)
        entity.followers += 1
        entity.save()
    else:
        bot_template.error_text(bot, msg)


def remove_command(bot, msg, user):
    entity_id = int(msg.message.text[8:])
    entity = tasks.get_entity(entity_id)
    if entity not in tasks.get_user_entity(user):
        bot_template.error_text(bot, msg, type='NoFallow')
        return

    if tasks.set_entity(user, entity_id, 0):
        bot_template.change_entity(bot, msg, entity, type=0)
        entity.followers -= 1
        entity.save()
    else:
        bot_template.error_text(bot, msg)


def list_command(bot, msg, user):
    bot_template.show_user_entity(bot, msg, user, tasks.get_user_entity(user))


def help_command(bot, msg, user):
    bot_template.bot_help(bot, msg, user)


def user_alert_handler(bot, job):
    bulk = UserAlert.objects.filter(is_sent=False)
    for item in bulk:
        bot_template.send_telegram_all_user(bot, item.text)
        item.is_sent = True
        item.save()


def start_command(bot, msg, new_user):
    if new_user:
        bot_template.welcome_text(bot, msg)
    else:
        bot_template.error_text(bot, msg, type="RepetitiveStart")


def news_command(bot, msg, user):
    news_id = command_separator(msg, 'add')
    try:
        news = News.objects.get(id=news_id)
        bot_template.publish_news(bot, news, user, page=1, message_id=None)
    except News.DoesNotExist:
        return bot_template.error_text(bot, msg, 'NoneNews')


def command_separator(msg, command):
    return int(msg.message.text[len(command)+3:])


# TODO news suumary and complete news, ...

