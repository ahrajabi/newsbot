from django.utils import timezone
from telegrambot import bot_template
from entities import tasks
import re
import datetime
import sys
from django.contrib.auth.models import User
from telegrambot.models import UserAlert
thismodule = sys.modules[__name__]

from .models import UserProfile

def handle(bot, msg):
    user = getUser(msg.message.from_user.id)
    text = msg.message.text
    entity = tasks.get_entity_contain(msg.message.text)
    if entity == None:
        bot_template.error_text(bot, msg,'NoEntity')
    else:
        bot_template.show_entities(bot, msg, user, entity)



def welcome_bot(bot, msg):
    user = User.objects.create_user(username=msg.message.from_user.username)
    up = user.userprofile_set.create(first_name=msg.message.from_user.first_name,
                                     last_name=msg.message.from_user.last_name,
                                     last_chat=timezone.now(),
                                     telegram_id=msg.message.from_user.id,
                                     )

    bot_template.welcome_text(bot, msg)
    return user


def verifyUser(bot,msg):
    user = getUser(msg.message.from_user.id)
    if not user:
        user = welcome_bot(bot, msg)
    return user


def getUser(telegramid):
    profiles = UserProfile.objects.filter(telegram_id= telegramid)
    if not profiles:
        return False
    user = [ i.user for i in profiles][0]
    if not user:
        return None
    return user


def add_command(bot, msg,user):
    entity_id = int(msg.message.text[5:])
    entity = tasks.get_entity(entity_id)
    if entity in tasks.get_user_entity(user):
        bot_template.error_text(bot, msg, type='PriorFallow')
        return
    if tasks.set_entity(user, entity_id, 'Fallow'):
        bot_template.change_entity(bot, msg, entity, type='fallow')
        entity.followers +=1
        entity.save()
    else:
        bot_template.error_text(bot, msg)


def remove_command(bot, msg,user):
    entity_id = int(msg.message.text[8:])
    entity = tasks.get_entity(entity_id)
    if not entity in tasks.get_user_entity(user):
        bot_template.error_text(bot, msg, type='NoFallow')
        return

    if tasks.set_entity(user, entity_id, 'Unfallow'):
        bot_template.change_entity(bot, msg, entity, type='unfallow')
        entity.followers -= 1
        entity.save()
    else:
        bot_template.error_text(bot, msg)


def list_command(bot, msg,user):
    bot_template.show_user_entity(bot, msg,user,tasks.get_user_entity(user))


def help_command(bot, msg,user):
    bot_template.help(bot, msg,user)


def user_alert_handler(bot,job):
    bulk = UserAlert.objects.filter(is_sent=False)#,send_time__gte=datetime.datetime.now())
    for item in bulk:
        bot_template.send_telegram_alluser(bot, item.text)
        item.is_sent = True
        item.save()