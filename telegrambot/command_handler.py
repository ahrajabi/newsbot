# -*- coding: utf-8 -*-
import sys
from telegram.emoji import Emoji
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from datetime import timedelta

from entities import tasks
from rss.models import News
from telegrambot import bot_template
from telegrambot.models import UserAlert, UserProfile, UserSettings
from telegrambot.bot_send import send_telegram_user, error_text, send_telegram_all_user, send_telegram_document
thismodule = sys.modules[__name__]


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
    if len(msg.message.chat.username) > 0:
        username = msg.message.chat.username
    else:
        username = msg.message.chat.id


    user = User.objects.create_user(username=username)

    try:
        user.userprofile_set.create(first_name=msg.message.chat.first_name,
                                    last_name=msg.message.chat.last_name,
                                    last_chat=timezone.now(),
                                    telegram_id=msg.message.chat.id)
    except Exception:
        user.userprofile_set.create(last_chat=timezone.now(),
                                    telegram_id=msg.message.from_user.id)

    get_user(msg.message.from_user.id)
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
        all_profile = UserProfile.objects.all()
        for profile in all_profile:
            id = profile.telegram_id
            if id:
                send_telegram_user(bot, profile.user, item.text)

        item.is_sent = True
        item.save()


def start_command(bot, msg, new_user, user):
    inp = msg.message.text.split(' ')

    if new_user:
        bot_template.welcome_text(bot, msg, user)
    else:
        up = UserProfile.objects.get(user=user)
        if up and up.stopped:
            up.stopped = False
            up.save()
        text = '''
        حساب شما مجددا فعال شد.
        '''
        send_telegram_user(bot, user, text, msg)
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
        return error_text(bot, msg, user, 'NoneNews')


def command_separator(msg, command):
    return int(msg.message.text[len(command)+3:])


def live_command(bot, msg, user):
    user_settings = UserProfile.objects.get(user=user).user_settings
    live_news_status = user_settings.live_news
    if not live_news_status:
        user_settings.live_news = True
        user_settings.save()
        text = Emoji.WHITE_HEAVY_CHECK_MARK + ''' ارسال اخبار به صورت بر خط فعال شد.\n
   از این پس اخبار مرتبط با موضوع های مورد علاقه شما به صورت لحظه ای ارسال می شود.'''
    else:
        text = 'ارسال اخبار به صورت بر خط فعال است.'
    send_telegram_user(bot, user, text, msg)


def chrome_command(bot, msg, user):
    commands = ['/extension', '/token']
    response = Emoji.SMALL_BLUE_DIAMOND + '''شما میتوانید با نصب افزونه خبرمن اخبار را از طریق مرورگر Google Chrome خود دریافت کنید.
    کافیست دو مرحله زیر را انجام دهید :
    افزونه خبر من را دریافت و نصب کنید %s
    نام کاربری و توکن خود را دریافت کنید %s
    ''' % (commands[0], commands[1])
    send_telegram_user(bot, user, response, msg)


def extension_command(bot, msg, user):
    # file = ''
    # send_telegram_document(bot, user, msg, file)
    text = 'افزونه خبر من به زودی اضافه میشود.'
    send_telegram_user(bot, user, text, msg)

def token_command(bot, msg, user):
    if not user.username:
        response = '''جهت استفاده از افزونه باید برای حساب کاربری تلگرام خود نام کاربردی تعریف کنید
        نام کاربری خود را از طریق تنظیمات تلگرام ایجاد کنید و برای دریافت توکن مجددا اقدام کنید.
        '''
    else:
        user_token, is_new = Token.objects.get_or_create(user=user)
        if is_new:
            response =Emoji.THUMBS_UP_SIGN + 'توکن با موفقیت ایجاد شد :)\n '
        else:
            response = 'شما قبلا توکن را ایجاد کرده بودید ، اطلاعات شما:\n'
        response += 'نام کاربری : %s \n توکن : %s ' % (user.username, user_token)
    send_telegram_user(bot, user, response, msg)


def newslist_command(bot, msg, user):
    from telegrambot.publish import prepare_periodic_publish_news
    up = UserProfile.objects.get(user=user)
    prepare_periodic_publish_news(bot, 0, up)


def special_command(bot, msg, user):
    delta = timezone.now() - timedelta(hours=20)
    exl = ['irna', 'mehrnews', 'fars', 'tasnim', 'codal', 'isna', 'shana', 'akhbarrasmi', 'sena', 'boursenews', 'naftema']
    news = News.objects.filter(base_news__published_date__range=(delta, timezone.now())) \
        .exclude(base_news__news_agency__name__in=exl) \
        .order_by('?')

    if not news:
        return error_text(bot, msg, user, 'NoneNews')
    news = news[0]
    try:
        bot_template.publish_news(bot, news, user, page=1, message_id=None)
    except News.DoesNotExist:
        return error_text(bot, msg, user, 'NoneNews')

    print('special_command')


def stoplive_command(bot, msg, user):
    user_settings = UserProfile.objects.get(user=user).user_settings
    live_news_status = user_settings.live_news
    if live_news_status:
        user_settings.live_news = False
        user_settings.save()
        text = Emoji.CROSS_MARK + 'ارسال اخبار به صورت بر خط قطع شد'
    else:

        text = 'ارسال اخبار به صورت بر خط غیرفعال است.'
    send_telegram_user(bot, user, text, msg)


def contact_command(bot, msg, user):
    text = 'با ما در تماس باشید:\n'
    text += Emoji.MEMO + '@KhabareMan'
    send_telegram_user(bot, user, text, msg)