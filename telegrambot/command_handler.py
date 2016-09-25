# -*- coding: utf-8 -*-
import sys
from telegram.emoji import Emoji
from django.utils import timezone
from telegram import InlineKeyboardMarkup
from django.contrib.auth.models import User
from telegram.inlinekeyboardbutton import InlineKeyboardButton


from entities import tasks
from rss.models import News
from entities.models import Entity
from telegrambot import bot_template
from telegrambot.models import UserAlert, UserProfile, UserSettings
from rss.ml import normalize, word_tokenize, bi_gram, tri_gram
from telegrambot.bot_template import prepare_advice_entity_link
from telegrambot.news_template import prepare_multiple_sample_news
from rss.elastic import elastic_search_entity, similar_news_to_query
from telegrambot.bot_send import send_telegram_user, error_text, send_telegram_all_user
from newsbot.settings import SAMPLE_NEWS_COUNT, MIN_HITS_ENTITY_VALIDATION, DAYS_FOR_SEARCH_NEWS
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

def deactive_profile(up):
    up.activated = False
    up.save()

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

    ##
    up = UserProfile.objects.get(user=user)
    if up:
        up.last_chat = timezone.now()
        up.activated = True
        if not up.user_settings:
            up.user_settings = UserSettings.objects.create()

    up.save()
    ##
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


def start_command(bot, msg, new_user, user):
    inp = msg.message.text.split(' ')

    if new_user:
        bot_template.welcome_text(bot, msg)
    else:
        up = UserProfile.objects.get(user=user)
        if up and up.stopped:
            up.stopped = False
            up.save()
        text = '''
        حساب شما مجددا فعال شد.
        '''
        send_telegram_user(bot, user, text)
    if inp[1]:
        arg = inp[1]

        if arg.startswith('N'):
            try:
                news = News.objects.get(id=arg[1:])
                bot_template.publish_news(bot, news, user, page=1)
            except News.DoesNotExist:
                return error_text(bot, msg, 'NoneNews')


def stop_command(bot, msg, user):
    up = UserProfile.objects.get(user=user)
    if up and not up.stopped:
        up.stopped = True
        up.save()
        text = '''
        حساب شما متوقف شد.
        '''
        send_telegram_user(bot, user, text)


def news_command(bot, msg, user):
    news_id = command_separator(msg, 'add')
    try:
        news = News.objects.get(id=news_id)
        bot_template.publish_news(bot, news, user, page=1, message_id=None, user_entity=tasks.get_user_entity(user))
    except News.DoesNotExist:
        return error_text(bot, msg, 'NoneNews')


def command_separator(msg, command):
    return int(msg.message.text[len(command)+3:])


def search_box_result(bot, msg, user, msg_id=None, text=None):

    if not text:
        text = normalize(msg.message.text)
    hits = elastic_search_entity(text, max(MIN_HITS_ENTITY_VALIDATION, SAMPLE_NEWS_COUNT) + 1)

    response = ""

    no_response = False
    elastic_query = '0'
    if hits:
        h_response, h_response_len = prepare_multiple_sample_news(list(map(int, [hit['_id'] for hit in hits])),
                                                                  SAMPLE_NEWS_COUNT)
        if len(hits) >= MIN_HITS_ENTITY_VALIDATION:
            entity = Entity.objects.get_or_create(name=text, wiki_name='')[0]
            response += "%s خبرهای مرتبط با دسته فوق:\n" % Emoji.NEWSPAPER + h_response + '\n'
            response += Emoji.HEAVY_MINUS_SIGN * 5 + '\n'+ Emoji.BOOKMARK + \
                        "با انتخاب دسته زیر ، اخبار مرتبط به صورت بر خط برای شما ارسال خواهد شد." + \
                        '\n'+ prepare_advice_entity_link(entity)
        else:
            no_response = True

    if not hits or no_response:
        elastic_query = '1'
        similar_news_id = similar_news_to_query(text, SAMPLE_NEWS_COUNT, DAYS_FOR_SEARCH_NEWS)
        similar_news = prepare_multiple_sample_news(similar_news_id, 2)[0]
        response += Emoji.NEWSPAPER + "خبرهای مشابه \n" + similar_news + '\n'

        def print_n_gram(n_gram):
            gram_response = ""
            not_response = True
            for word in n_gram:
                related_hits = elastic_search_entity(word, MIN_HITS_ENTITY_VALIDATION)
                if len(related_hits) >= MIN_HITS_ENTITY_VALIDATION:
                    en = Entity.objects.get_or_create(name=word, wiki_name='')[0]
                    gram_response += prepare_advice_entity_link(en) + '\n'
                    not_response = False

            return not_response, gram_response
        pre_response = Emoji.HEAVY_MINUS_SIGN * 5 + '\n'+ \
                       Emoji.WARNING_SIGN + "متن وارد شده یافت نشد.\n" + Emoji.BOOKMARK + \
                       "دسته های مشابه پیشنهادی:‌\n با انتخاب هر یک اخبار مرتبط به صورت بر خط برای شما ارسال خواهد شد.\n"

        three_gram = tri_gram(text)
        no_three_gram_response, three_response = print_n_gram(three_gram)
        if no_three_gram_response:
            two_gram = bi_gram(text)
            no_two_gram_response, two_response = print_n_gram(two_gram)
            if no_two_gram_response:
                one_gram = word_tokenize(text)
                no_one_gram_response, one_response = print_n_gram(one_gram)
                if no_one_gram_response:
                    if not similar_news_id:
                        error_text(bot, msg, 'InvalidEntity')
                        return
                else:
                    response += pre_response + one_response
            else:
                response += pre_response + two_response
        else:
            response += pre_response + three_response

    final_destination = None
    call_back_id = None
    if msg.callback_query is not None:
        final_destination = msg.callback_query.message.message_id
        call_back_id = msg_id
    elif msg.message is not None:
        call_back_id = msg.message.message_id

    buttons = [[
        InlineKeyboardButton(text='صفحه بعد', callback_data='continue-' + 'next-1-' + elastic_query +
                                                            '-' + str(call_back_id)),
    ], ]
    keyboard = InlineKeyboardMarkup(buttons)

    if len(hits) == SAMPLE_NEWS_COUNT:
        keyboard = None

    send_telegram_user(bot, user, response, keyboard, final_destination)
