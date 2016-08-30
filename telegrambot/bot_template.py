# -*- coding: utf-8 -*-
import telegram
from entities import tasks
from telegram.emoji import Emoji
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from django.contrib.auth.models import User

from telegrambot.models import UserProfile
from entities.models import Entity
from entities.tasks import get_user_entity


def welcome_text(bot, msg):
    keyboard = ReplyKeyboardMarkup(keyboard=[[
        '/HELP ⁉️ راهنمایی',
         ]], resize_keyboard=True)
    # TODO insert bot name in below text
    text = '''
        سلام %s به بات خبری خوش آمدید.
        از این پس می توانید اخبار مرتبط با موضوعات مورد علاقه خود را به راحتی دریافت کنید.
        برای شروع لطفا موضوعات مورد علاقه خود را(به عنوان مثال: تهران) از طریق کادر پایین ارسال کنید%s

        ''' % (Emoji.RAISED_HAND, Emoji.WHITE_DOWN_POINTING_BACKHAND_INDEX)
    send_telegram(bot, msg, text, keyboard)


def show_entities(bot, msg,user, entities):
    keyboard = None
    text = ''
    button = list()
    for item in entities:
        text += tasks.get_link(user, item) + '\n'
    #    button.append([InlineKeyboardButton(text=item.name, callback_data="data")])
    #keyboard = InlineKeyboardMarkup(inline_keyboard=button)
    return send_telegram(bot, msg, text, keyboard)


def show_user_entity(bot, msg, user, entities):
    if entities:
        text = 'دسته هایی که آن ها را دنبال میکنید:\n'
        for i in entities:
            text += tasks.get_link(user, i) + '\n'
    else:
        text = ''' شما دسته ای را دنبال نمیکنید %s
        می توانید موضوعات مورد علاقه خود را(به عنوان مثال: تهران) از طریق کادر پایین ارسال کنید%s
        ''' % (Emoji.FACE_SCREAMING_IN_FEAR, Emoji.WHITE_DOWN_POINTING_BACKHAND_INDEX)
    send_telegram(bot, msg, text, None)


def change_entity(bot, msg, entity , type = 'fallow' ):
    buttons = [[
        InlineKeyboardButton(text='۱', callback_data='score-'+str(entity.id)+'-(-2)'),
        InlineKeyboardButton(text='۲', callback_data='score-'+str(entity.id)+'-(-1)'),
        InlineKeyboardButton(text='۳', callback_data='score-'+str(entity.id)+'-(0)'),
        InlineKeyboardButton(text='۴', callback_data='score-'+str(entity.id)+'-(1)'),
        InlineKeyboardButton(text='۵', callback_data='score-'+str(entity.id)+'-(2)'),
         ],]
    keyboard = InlineKeyboardMarkup(buttons)
    if type == 'fallow':
        TEXT = '''
دسته %s نظر اضافه شد.
برای حذف کردن بر روی لینک %s کلیک کنید.
        ''' % (entity.name, "/remove_"+str(entity.id))
        return send_telegram(bot, msg, TEXT, keyboard)
    else:
        TEXT = '''
        دسته %s حذف شد.
        برای اضافه کردن مجدد بر روی لینک %s کلیک کنید.
        ''' % (entity.name,"/add_"+str(entity.id))
        return send_telegram(bot, msg, TEXT, keyboard)


def error_text(bot, msg, type = None):
    TEXT = 'ERROR'
    if type == 'NoEntity':
        TEXT = '''
        دسته مورد نظر موجود نمی‌باشد.
        '''
    elif type == 'LongMessage':
        TEXT= '''
        نتیجه درخواست شما بسیار طولانی است.
        و امکان ارسال آن وجود ندارد.
        '''
    elif type =='NoCommand':
        TEXT='''
        <b>همچین دستوری تعریف نشده است.</b>
        '''
    elif type =='PriorFallow':
        TEXT = '''
        شما قبلا این دسته را اضافه کرده اید.
        '''
    elif type == 'NoFallow':
        TEXT = '''
        شما این دسته را دنبال نمی کرده اید.
        '''
    elif type == 'InvalidEntity':
        TEXT = ''' دسته اضافه شده مورد قبول نیست '''
    return send_telegram(bot, msg, TEXT, None)

def help(bot, msg,user):
    menu = [
        ('/list' , 'تمام دسته هایی که عضو شده اید.'),
        ('/help', 'صفحه‌ی راهنمایی'),
        ('/live' ,'مشاهده‌ی اخبار به صورت لحظه‌ای'),
    ]
    text = 'راهنمایش ربات'+'\n'
    for i in menu:
        text += i[0] + ' ' + '<i>' + i[1] +'</i>\n'
    send_telegram_user(bot, user, text, None)


def news_page(News, page=1):
    buttons = [[
        InlineKeyboardButton(text='پسند', callback_data='news-' + str(News.id) + '-like')],
        [
            InlineKeyboardButton(text='خلاصه', callback_data='news-' + str(News.id) + '-overview'),
            InlineKeyboardButton(text='متن کامل خبر', callback_data='news-' + str(News.id) + '-full'),
            InlineKeyboardButton(text='آمار', callback_data='news-' + str(News.id) + '-stat'),
    ], ]
    keyboard = InlineKeyboardMarkup(buttons)
    TEXT = News.base_news.title + '\n'
    if page == 1:
        TEXT += News.summary + '\n'
    elif page == 2:
        TEXT += News.body[0:1000] + '\n' + 'ادامه دارد'
    elif page == 3:
        TEXT += str(News.pic_number) + '\n'
    TEXT = TEXT + '@mybot بات من'
    return keyboard, TEXT

def publish_news(bot, News, User, page=1, message_id=None):
    try:
        keyboard, Text = news_page(News, page)
    except Exception:
        send_telegram_user(bot, User, Text, keyboard, message_id)

def send_telegram(bot, msg, Text , keyboard=None):
    if len(Text) > 4096 :
        error_text(msg,type="LongMessage")
        return False
    return bot.sendMessage(chat_id=msg.message.chat_id,
                           text = Text,
                           reply_markup=keyboard,
                           parse_mode =telegram.ParseMode.HTML)


def send_telegram_user(bot, User, Text , keyboard=None, message_id=None):
    profile = UserProfile.objects.get(user=User)
    id = profile.telegram_id
    if id:
        if not message_id:
            return bot.sendMessage(chat_id=id,
                               text = Text,
                               reply_markup=keyboard,
                               parse_mode = telegram.ParseMode.HTML)
        else:
            bot.editMessageText(text=Text,
                                chat_id=id,
                                message_id=message_id,
                                reply_markup=keyboard,
                                parse_mode=telegram.ParseMode.HTML,
                                inline_message_id=None)


def send_telegram_alluser(bot, Text , keyboard=None, Photo=None):
    allprofile = UserProfile.objects.all()
    for profile in allprofile:
        id = profile.telegram_id
        if id:
            if Photo:
                bot.sendPhoto(chat_id=id,
                              photo=Photo,
                              caption=Text[0:199],
                              reply_markup=keyboard,
                              parse_mode=telegram.ParseMode.HTML)
            else:
                bot.sendMessage(chat_id=id,
                                   text = Text,
                                   reply_markup=keyboard,
                                   parse_mode = telegram.ParseMode.HTML)


def after_user_add_entity(bot, msg, user, entity, entities):
    text = "دسته ' %s ' اضافه شد %s" % (entity, Emoji.WINKING_FACE)
    entity.followers += 1
    send_telegram(bot, msg, text)
    show_user_entity(bot, msg, user, entities)


def entity_recommendation():
    return Entity.objects.order_by('followers')[:5]
