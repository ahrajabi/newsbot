from telegram.emoji import Emoji
from django.utils import timezone
from telegram.error import Unauthorized
from rest_framework.authtoken.models import Token
from datetime import timedelta
from telegram import InlineKeyboardMarkup
from telegram.inlinekeyboardbutton import InlineKeyboardButton

from entities import tasks
from entities.models import Entity
from rss.models import News
from telegrambot import bot_template
from telegrambot.models import UserAlert, UserProfile
from telegrambot.bot_send import send_telegram_user, error_text


def deactive_profile(up):
    up.activated = False
    up.save()


def add_command(bot, update, user):
    entity_id = int(update.message.text[5:])
    try:
        entity = Entity.objects.get(id=entity_id)
    except Entity.DoesNotExist:
        entity = None

    if entity in tasks.get_user_entity(user):
        error_text(bot, update, user, error_type='PriorFollow')
        return
    if tasks.set_entity(user, entity_id, 1):
        bot_template.change_entity(bot, update, entity, user, change_type=True)
        entity.followers += 1
        entity.save()
    else:
        error_text(bot, update, user)


def remove_command(bot, update, user):
    entity_id = int(update.message.text[8:])

    try:
        entity = Entity.objects.get(id=entity_id)
    except Entity.DoesNotExist:
        entity = None

    if entity not in tasks.get_user_entity(user):
        error_text(bot, update, user, error_type='NoFallow')
        return

    if tasks.set_entity(user, entity_id, 0):
        bot_template.change_entity(bot, update, entity, user, change_type=False)
        entity.followers -= 1
        entity.save()
    else:
        error_text(bot, update, user)


def list_command(bot, update, user):
    bot_template.show_user_entity(bot, update, user, tasks.get_user_entity(user))


def help_command(bot, update, user):
    bot_template.bot_help(bot, update, user)


def user_alert_handler(bot, job):
    del job
    bulk = UserAlert.objects.filter(is_sent=False)
    for item in bulk:
        all_profile = UserProfile.objects.all()
        for profile in all_profile:
            pid = profile.telegram_id
            if pid:
                try:
                    send_telegram_user(bot, profile.user, item.text)
                except Unauthorized:
                    pass

        item.is_sent = True
        item.save()


def stop_command(bot, update, user):
    del update
    up = UserProfile.objects.get(user=user)
    if up and not up.stopped:
        up.stopped = True
        up.save()
        text = '''
        حساب شما متوقف شد.
        برای فعال سازی مجدد حساب خود /active را لمس نمایید.
        '''
        send_telegram_user(bot, user, text)


def active_command(bot, update, user):
    del update
    up = UserProfile.objects.get(user=user)
    if up and up.stopped:
        up.stopped = False
        up.save()
        text = '''
        حساب شما فعال شد.
        '''
        send_telegram_user(bot, user, text)


def news_command(bot, update, user):
    news_id = command_separator(update, 'add')
    try:
        news = News.objects.get(id=news_id)
        bot_template.publish_news(bot, news, user, page=1, message_id=None, user_entity=tasks.get_user_entity(user))
    except News.DoesNotExist:
        return error_text(bot, update, user, 'NoneNews')


def command_separator(update, command):
    return int(update.message.text[len(command) + 3:])


# def live_command(bot, update, user):
#     if not tasks.get_user_entity(user):
#         return error_text(bot, update, user, 'NoneEntity')
#     user_settings = UserProfile.objects.get(user=user).user_settings
#     live_news_status = user_settings.live_news
#     if not live_news_status:
#         user_settings.live_news = True
#         user_settings.save()
#         text = Emoji.WHITE_HEAVY_CHECK_MARK + ''' ارسال اخبار نشان‌ها به صورت بر خط فعال شد.\n
#    از این پس اخبار نشان‌ها به صورت لحظه ای ارسال می شود.'''
#     else:
#         text = 'ارسال اخبار نشان‌ها به صورت بر خط فعال است.'
#     send_telegram_user(bot, user, text, update)


def browser_command(bot, update, user):
    commands = ['/extension', '/token']
    response = Emoji.SMALL_BLUE_DIAMOND + '''شما میتوانید با نصب
    <b>افزونه‌ی خبرمن</b>، اخبار را از طریق مرورگر گوگل کروم خود دریافت نمایید.

    کافیست دو مرحله زیر را انجام دهید :
1⃣ افزونه خبر من را از طریق <a href='https://chrome.google.com/webstore/detail/khabare-man/lbjgcnoliaijdlncdjcpgbnjagjbbcld'>این لینک</a> با مرورگر گوگل کروم دریافت و نصب کنید.

2⃣ نام کاربری و توکن خود را با لمس بر روی %s دریافت نمایید.

    ''' % commands[1]
    send_telegram_user(bot, user, response, update, ps=False)


def extension_command(bot, update, user):
    text = 'افزونه خبر من به زودی اضافه میشود.'
    send_telegram_user(bot, user, text, update)


def token_command(bot, update, user):
    if not user.username:
        response = '''جهت استفاده از افزونه باید برای حساب کاربری تلگرام خود نام کاربردی تعریف کنید
        نام کاربری خود را از طریق تنظیمات تلگرام ایجاد کنید و برای دریافت توکن مجددا اقدام کنید.
        '''
    else:
        user_token, is_new = Token.objects.get_or_create(user=user)
        if is_new:
            response = Emoji.THUMBS_UP_SIGN + 'توکن با موفقیت ایجاد شد :)\n '
        else:
            response = 'شما قبلا توکن را ایجاد کرده بودید ، اطلاعات شما:\n'
        response += 'نام کاربری : %s \n توکن : %s ' % (user.username, user_token)
    send_telegram_user(bot, user, response, update)


def newslist_command(bot, update, user):
    if not tasks.get_user_entity(user):
        return error_text(bot, update, user, 'NoneEntity')
    from telegrambot.publish import prepare_periodic_publish_news
    up = UserProfile.objects.get(user=user)
    prepare_periodic_publish_news(bot, 0, up, alert_no_news=True)


# def special_command(bot, update, user):
#     delta = timezone.now() - timedelta(hours=20)
#     # exl = ['irna', 'mehrnews', 'fars', 'tasnim', 'codal', 'isna', 'shana',
#     #  'akhbarrasmi', 'sena', 'boursenews', 'naftema']
#     exl = []
#     up = UserProfile.objects.get(user=user)
#
#     if up.interest_categories.all().count() == 0:
#         return error_text(bot, update, user, 'NoCategory')
#
#     news = News.objects.filter(base_news__published_date__range=(delta, timezone.now()),
#                                base_news__all_rss__category_ref__in=up.interest_categories.all()) \
#         .exclude(base_news__news_agency__name__in=exl) \
#         .order_by('?')
#
#     if not news:
#         return error_text(bot, update, user, 'NoNews')
#     news = news[0]
#     try:
#         bot_template.publish_news(bot, news, user, page=1, message_id=None)
#     except News.DoesNotExist:
#         return error_text(bot, update, user, 'NoneNews')


# def stoplive_command(bot, update, user):
#     user_settings = UserProfile.objects.get(user=user).user_settings
#     live_news_status = user_settings.live_news
#     if live_news_status:
#         user_settings.live_news = False
#         user_settings.save()
#         text = Emoji.CROSS_MARK + 'ارسال اخبار به صورت بر خط قطع شد'
#     else:
#
#         text = 'ارسال اخبار به صورت بر خط غیرفعال است.'
#     send_telegram_user(bot, user, text, update)


def contact_command(bot, update, user):
    text = 'با ما در تماس باشید:\n'
    text += Emoji.MEMO + '@KhabareMan'
    send_telegram_user(bot, user, text, update)


def interval_command(bot, update, user):
    current_interval = UserProfile.objects.get(user=user).user_settings.interval_news_list
    if current_interval < 60:
        time = current_interval
        time_type = 'دقیقه'
    else:
        time = int(current_interval / 60)
        time_type = 'ساعت'
    text = 'شما هم‌اکنون اخبار جدید را هر %d %s دریافت می‌کنید.\n' % (time, time_type)
    text += 'تمایل دارید اخبار زنده با چه فاصله‌ی زمانی برای شما ارسال شود؟'
    buttons = [
        [InlineKeyboardButton(text='۱ ساعت', callback_data='interval-60'),
         InlineKeyboardButton(text='۳۰ دقیقه', callback_data='interval-30'),
         InlineKeyboardButton(text='۱۰ دقیقه', callback_data='interval-10')
         ],
        [InlineKeyboardButton(text='۲۴ ساعت', callback_data='interval-1440'),
         InlineKeyboardButton(text='۵ ساعت', callback_data='interval-300'),
         InlineKeyboardButton(text='۳ ساعت', callback_data='interval-180')
         ], ]

    keyboard = InlineKeyboardMarkup(buttons)
    send_telegram_user(bot, user, text, update, keyboard)
