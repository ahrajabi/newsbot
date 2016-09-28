# -*- coding: utf-8 -*-
import sys
from telegram.emoji import Emoji
from django.utils import timezone
from telegram import InlineKeyboardMarkup
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from telegram.inlinekeyboardbutton import InlineKeyboardButton


from entities import tasks
from rss.models import News
from entities.models import Entity
from telegrambot import bot_template
from rss.ml import normalize, word_tokenize, bi_gram, tri_gram
from telegrambot.bot_template import prepare_advice_entity_link
from telegrambot.news_template import prepare_multiple_sample_news
from telegrambot.models import UserAlert, UserProfile, UserSettings
from rss.elastic import elastic_search_entity, similar_news_to_query
from newsbot.settings import SAMPLE_NEWS_COUNT, MIN_HITS_ENTITY_VALIDATION, DAYS_FOR_SEARCH_NEWS
from telegrambot.bot_send import send_telegram_user, error_text, send_telegram_all_user, send_telegram_document
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
        error_text(bot, msg, user, type='PriorFollow')
        return
    if tasks.set_entity(user, entity_id, 1):
        bot_template.change_entity(bot, msg, entity,user, type=1)
        entity.followers += 1
        entity.save()
    else:
        error_text(bot, msg, user)


def remove_command(bot, msg, user):
    entity_id = int(msg.message.text[8:])
    entity = tasks.get_entity(entity_id)
    if entity not in tasks.get_user_entity(user):
        error_text(bot, msg, user, type='NoFallow')
        return

    if tasks.set_entity(user, entity_id, 0):
        bot_template.change_entity(bot, msg, entity, user, type=0)
        entity.followers -= 1
        entity.save()
    else:
        error_text(bot, msg, user)


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
    if new_user:
        bot_template.welcome_text(bot, msg, user)
    else:
        error_text(bot, msg, user, type="RepetitiveStart")


def news_command(bot, msg, user):
    news_id = command_separator(msg, 'add')
    try:
        news = News.objects.get(id=news_id)
        bot_template.publish_news(bot, news, user, page=1, message_id=None, user_entity=tasks.get_user_entity(user))
    except News.DoesNotExist:
        return error_text(bot, msg, user, 'NoneNews')


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
            response += Emoji.BOOKMARK + \
                        "با انتخاب دسته زیر ، اخبار مرتبط به صورت بر خط برای شما ارسال خواهد شد." + \
                        '\n'+ prepare_advice_entity_link(entity)
            response += '\n' + Emoji.HEAVY_MINUS_SIGN * 5 + '\n' + "%s خبرهای مرتبط با دسته فوق:\n" % Emoji.NEWSPAPER + h_response + '\n'

        else:
            no_response = True

    if not hits or no_response:
        elastic_query = '1'
        similar_news_id = similar_news_to_query(text, SAMPLE_NEWS_COUNT, DAYS_FOR_SEARCH_NEWS)
        similar_news = prepare_multiple_sample_news(similar_news_id, 2)[0]

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
        pre_response = Emoji.WARNING_SIGN + "متن وارد شده یافت نشد.\n" + Emoji.BOOKMARK + \
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
                        error_text(bot, msg, user, 'InvalidEntity')
                        return
                else:
                    response += pre_response + one_response
            else:
                response += pre_response + two_response
        else:
            response += pre_response + three_response

        response += '\n' + Emoji.HEAVY_MINUS_SIGN * 5 + '\n' + Emoji.NEWSPAPER + "خبرهای مشابه \n" + similar_news + '\n'

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

    send_telegram_user(bot, user, response, msg, keyboard, final_destination)


def live_command(bot, msg, user):
    user_settings = UserProfile.objects.get(user=user).user_settings
    live_news_status = user_settings.live_news
    if live_news_status:
        user_settings.live_news = False
        user_settings.save()
        text = Emoji.CROSS_MARK + 'ارسال اخبار به صورت بر خط قطع شد'
    else:
        user_settings.live_news = True
        user_settings.save()
        text = Emoji.WHITE_HEAVY_CHECK_MARK + ''' ارسال اخبار به صورت بر خط فعال شد.\n
   از این پس اخبار مرتبط با موضوع های مورد علاقه شما به صورت لحظه ای ارسال می شود'''

    send_telegram_user(bot, user, text, msg)


def chrome_command(bot, msg, user):
    commands = ['/extension', '/Token']
    response = '''شما میتوانید با نصب افزونه خبرمن اخبار را از طریق مرورگر Google Chrome خود دریافت کنید
    کافیست دو مرحله زیر را انجام دهید :
    افزونه خبر من را دریافت و نصب کنید %s
    نام کاربری و توکن خود را دریافت کنید %s
    ''' % (commands[0], commands[1])
    send_telegram_user(bot, user, response, msg)


def extension_command(bot, msg, user):
    file = ''
    send_telegram_document(bot, user, msg, file)


def token_command(bot, msg, user):
    if not user.username:
        response = '''جهت استفاده از افزونه باید برای حساب کاربری تلگرام خود نام کاربردی تعریف کنید
        نام کاربری خود را از طریق تنظیمات تلگرام ایجاد کنید و برای دریافت توکن مجددا اقدام کنید.
        '''
    else:
        user_token, is_new = Token.objects.get_or_create(user=user)
        if is_new:
            response = 'توکن با موفقیت ایجاد شد :)\n '
        else:
            response = 'شما قبلا توکن را ایجاد کرده بودید\n '
        response += 'نام کاربری : %s \n توکن : %s ' % (user.username, user_token)
    send_telegram_user(bot, user, response, msg)

