# -*- coding: utf-8 -*-
from telegram.emoji import Emoji
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegrambot.models import UserProfile
from entities import tasks
from entities.models import Entity
from newsbot.settings import PROJECT_EN_NAME, PROJECT_FA_NAME
from telegrambot.bot_send import send_telegram_user
from telegrambot.news_template import news_image_page, news_page


def welcome_text(bot, msg, user):
    text = '''
        سلام  %s %s
        به سرویس هوشمند %s خوش آمدید.
        ''' % (msg.message.from_user.first_name, Emoji.RAISED_HAND, PROJECT_FA_NAME)

    send_telegram_user(bot, user, text, msg, ps=False)


def show_entities(bot, msg, user, entities):
    keyboard = None
    text = ''
    button = list()
    for item in entities:
        text += tasks.get_link(user, item) + '\n'
        # button.append([InlineKeyboardButton(text=item.name, callback_data="data")])
    #keyboard = InlineKeyboardMarkup(inline_keyboard=button)
    return send_telegram_user(bot, user, text, msg, keyboard=keyboard)


def show_user_entity(bot, msg, user, entities):
    if entities:
        text = 'نشان‌هایی که دنبال می‌کنید:\n'
        for i in entities:
            text += tasks.get_link(user, i) + '\n'
    else:
        text = ''' شما هیچ نشانی را دنبال نمی‌کنید %s
        می‌توانید موضوعات مورد علاقه خود (مثل پتروشیمی) را تایپ %s و سپس با افزودن آن به لیست نشان‌ها، دنبال نمایید.
        ''' % (Emoji.FACE_SCREAMING_IN_FEAR, Emoji.WHITE_DOWN_POINTING_BACKHAND_INDEX)
    send_telegram_user(bot, user, text, msg)


def change_entity(bot, msg, entity, user, type=1):
    buttons = [[
        InlineKeyboardButton(text='۱', callback_data='score-'+str(entity.id)+'-(-2)'),
        InlineKeyboardButton(text='۲', callback_data='score-'+str(entity.id)+'-(-1)'),
        InlineKeyboardButton(text='۳', callback_data='score-'+str(entity.id)+'-(0)'),
        InlineKeyboardButton(text='۴', callback_data='score-'+str(entity.id)+'-(1)'),
        InlineKeyboardButton(text='۵', callback_data='score-'+str(entity.id)+'-(2)'),
         ], ]
    keyboard = InlineKeyboardMarkup(buttons)
    if type == 1:
        text = '''
دسته %s اضافه شد.
برای حذف کردن بر روی لینک %s کلیک کنید.
        ''' % (entity.name, "/remove_"+str(entity.id))
        # return send_telegram(bot, msg, text, keyboard)
        return send_telegram_user(bot, user, text, msg)
    else:
        text = '''
        دسته %s حذف شد.
        برای اضافه کردن مجدد بر روی لینک %s کلیک کنید.
        ''' % (entity.name, "/add_"+str(entity.id))
        # return send_telegram(bot, msg, text, keyboard)
        return send_telegram_user(bot, user, text, msg)


def bot_help(bot, msg, user):
    up = UserProfile.objects.get(user=user)
    if up.user_settings.live_news:
        live_news = ('/stoplive', 'توقف اخبار زنده',
                     'در حال حاضر اخبار مرتبط با نشان‌ها برای شما بلافاصله ارسال می‌شود. برای دریافت دوره‌ای اخبار این گزینه را لمس نمایید.')
    else:
        live_news = (
            '/live', 'اخبار زنده', 'از این طریق می‌توانید تمام خبرهای مرتبط با نشان‌های خود را بلافاصله دریافت نمایید.')

    menu = [
        # ('/categories', 'دسته‌بندی‌های خبری‌ شما'),
        ('/list', 'لیست نشان‌ها', 'با استفاده از این گزینه، می‌توانید نشان‌های خود را مشاهده و حذف نمایید.'),
        live_news,
        ('/browser', 'افزونه‌ی مرورگر',
         'این گزینه نحوه‌ی استفاده از افزونه‌ی مرورگر را توضیح می‌دهد. برای دریافت توکن و نام کاربری این گزینه را لمس نمایید.'),
        ('/contact', 'تماس با ما', 'راه‌های ارتباطی تیم خبرِمن')
    ]

    if up:
        if not up.stopped:
            menu.append(('/stop', 'توقف', 'توقف دریافت پیام از روبات'))
        else:
            menu.append(('/start',
                         'شما دریافت پیام از روبات را متوقف کرده اید. توسط این گزینه می توانید این محدودیت را بردارید.'))

    text = Emoji.LEFT_POINTING_MAGNIFYING_GLASS + 'راهنما' + '\n\n'

    for i in menu:
        text += Emoji.WHITE_RIGHT_POINTING_BACKHAND_INDEX + i[0] + ' ' + i[1] + '\n❔' + i[2] + '\n\n'
    send_telegram_user(bot, user, text, msg)


def publish_news(bot, news, user, page=1, message_id=None, **kwargs):
    try:
        news_image_page(bot, news, user, page=1, message_id=message_id)
    except:
        pass
    news_page(bot, news, user, page, message_id=message_id, **kwargs)


def after_user_add_entity(bot, msg, user, entity, entities):
    text = "دسته ' %s ' اضافه شد %s" % (entity, Emoji.PUSHPIN)
    send_telegram_user(bot, user, text, msg)
    show_user_entity(bot, msg, user, entities)


def entity_recommendation():
    return Entity.objects.order_by('followers')[:5]


def prepare_advice_entity_link(entity):
    return Emoji.SMALL_ORANGE_DIAMOND + "/add_"+str(entity.id)+" " + entity.name + ""


def show_related_entities(related_entities):
    text = Emoji.HEAVY_MINUS_SIGN * 6 + Emoji.WHITE_LEFT_POINTING_BACKHAND_INDEX + " دسته های مرتبط " +\
           Emoji.WHITE_RIGHT_POINTING_BACKHAND_INDEX + Emoji.HEAVY_MINUS_SIGN * 6
    text += '''
     %s نشان‌های مرتبط با متن وارد شده در زیر آمده است.
    با انتخاب هرکدام، می‌توانید اخبار مرتبط با آن را به صورت بر خط دنبال نمایید.\n''' % Emoji.BOOKMARK
    # for entity in (related_entities.sort(key=lambda e: e.followers, reverse=True)):
    for entity in related_entities:
        text += prepare_advice_entity_link(entity) + '\n'
    return text


# def send_related_entities(bot, msg, user, related_entities):
#     send_telegram(bot, msg, user, show_related_entities(related_entities))


def one_entity_recommendation(entity):
    text = ""
    text += Emoji.WHITE_DOWN_POINTING_BACKHAND_INDEX + '\n'
    text += prepare_advice_entity_link(entity)
    return text
