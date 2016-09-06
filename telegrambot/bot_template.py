# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup
from telegram.emoji import Emoji
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from entities import tasks
from rss.news import is_liked_news
from rss.elastic import more_like_this
from rss.models import News, ImageUrls
from telegrambot.models import UserNews
from rss.ml import normalize, sent_tokenize
from entities.models import Entity, NewsEntity
from telegrambot.news_template import sample_news_page
from newsbot.settings import BOT_NAME, PROJECT_EN_NAME
from telegrambot.bot_send import send_telegram, send_telegram_user


def welcome_text(bot, msg):
    keyboard = ReplyKeyboardMarkup(keyboard=[[
        '/HELP ⁉️ راهنمایی',
         ]], resize_keyboard=True)
    # TODO insert bot name in below text
    text = '''
        سلام %s به بات خبری %s خوش آمدید.
        از این پس می توانید اخبار مرتبط با موضوعات مورد علاقه خود را به راحتی دریافت کنید.
        برای شروع لطفا موضوعات مورد علاقه خود را(به عنوان مثال: تهران) از طریق کادر پایین ارسال کنید%s

        ''' % (Emoji.RAISED_HAND, PROJECT_EN_NAME, Emoji.WHITE_DOWN_POINTING_BACKHAND_INDEX)
    send_telegram(bot, msg, text, keyboard)


def show_entities(bot, msg, user, entities):
    keyboard = None
    text = ''
    button = list()
    for item in entities:
        text += tasks.get_link(user, item) + '\n'
        # button.append([InlineKeyboardButton(text=item.name, callback_data="data")])
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


def change_entity(bot, msg, entity, type=1):
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
        return send_telegram(bot, msg, text)
    else:
        text = '''
        دسته %s حذف شد.
        برای اضافه کردن مجدد بر روی لینک %s کلیک کنید.
        ''' % (entity.name, "/add_"+str(entity.id))
        # return send_telegram(bot, msg, text, keyboard)
        return send_telegram(bot, msg, text)


def bot_help(bot, msg, user):
    menu = [
        ('/list', 'تمام دسته هایی که عضو شده اید.'),
        ('/help', 'صفحه‌ی راهنمایی'),
        ('/live', 'مشاهده‌ی اخبار به صورت لحظه‌ای'),
    ]
    text = 'راهنمایش ربات'+'\n'
    for i in menu:
        text += i[0] + ' ' + '<i>' + i[1] + '</i>\n'
    send_telegram_user(bot, user, text, None)


def news_image_page(bot, news, user, page=1, message_id=None):
    keyboard = None
    image_url = ImageUrls.objects.filter(news=news)
    if not image_url:
        return
    image_url = image_url[0].img_url
    UserNews.objects.update_or_create(user=user, news=news, defaults={'image_page': page})
    text = news.base_news.title
    send_telegram_user(bot, user, text, keyboard, message_id, photo=image_url)


def news_page(bot, news, user, page=1, message_id=None, **kwargs):
    like = InlineKeyboardButton(text=Emoji.THUMBS_UP_SIGN + "(" + normalize(str(news.like_count)) + ")",
                                callback_data='news-' + str(news.id) + '-like')

    if is_liked_news(news=news, user=user):
        like = InlineKeyboardButton(text=Emoji.THUMBS_DOWN_SIGN + "(" + normalize(str(news.like_count)) + ")",
                                    callback_data='news-' + str(news.id) + '-unlike')

    buttons = [[like, ],
        [
            InlineKeyboardButton(text='خلاصه', callback_data='news-' + str(news.id) + '-overview'),
            InlineKeyboardButton(text='متن کامل خبر', callback_data='news-' + str(news.id) + '-full'),
            InlineKeyboardButton(text='اخبار مرتبط', callback_data='news-' + str(news.id) + '-stat'),
            InlineKeyboardButton(text='لینک خبر', url=str(news.base_news.url)),
    ], ]

    keyboard = InlineKeyboardMarkup(buttons)
    text = ''
    if page == 1:
        summary = news.summary
        has_summary = True

        if not summary:
            summary = news.body[:500]
            has_summary = False

        for sentence in sent_tokenize(summary):
            text += Emoji.SMALL_BLUE_DIAMOND + sentence + '\n'
            if len(text) > 300 and not has_summary:
                break
        text += '\n' + Emoji.WHITE_HEAVY_CHECK_MARK + 'منبع:‌ ' + news.base_news.rss.fa_name + '\n'

        if 'user_entity' in kwargs:
            news_user_entity = NewsEntity.objects.filter(news=news, entity__in=kwargs['user_entity'])
            if news_user_entity:
                text += '\n' + Emoji.BOOKMARK + ' به خاطر دسته های زیر این خبر را دریافت کردید:\n'
                for en in news_user_entity:
                    text += en.entity.name + ', '
                text += '\n'

    elif page == 2:
        text += Emoji.PUBLIC_ADDRESS_LOUDSPEAKER + news.base_news.title + '\n\n    '
        text += news.body[0:1000] + '\n' + 'ادامه دارد...' + '\n'
    elif page == 3:
        related = more_like_this(news.base_news.title, 5)
        for item in related:
            try:
                text += sample_news_page(News.objects.get(id=item))
            except:
                pass
        # text += '----------------\n'
        # text += 'منبع خبر' + news.base_news.rss.fa_name + '\n'
        # text += 'تاریخ ارسال' + str(news.base_news.published_date) + '\n'

    text += BOT_NAME

    send_telegram_user(bot, user, text, keyboard, message_id)
    UserNews.objects.update_or_create(user=user, news=news, defaults={'page': page})


def publish_news(bot, news, user, page=1, message_id=None, **kwargs):
    news_image_page(bot, news, user, page=1, message_id=message_id)
    news_page(bot, news, user, page, message_id=message_id, **kwargs)


def after_user_add_entity(bot, msg, user, entity, entities):
    text = "دسته ' %s ' اضافه شد %s" % (entity, Emoji.PUSHPIN)
    send_telegram(bot, msg, text)
    show_user_entity(bot, msg, user, entities)


def entity_recommendation():
    return Entity.objects.order_by('followers')[:5]


def show_related_entities(related_entities):
    text = ''' %s دسته های مرتبط با متن وارد شده در زیر آمده است.
    با انتخاب هرکدام، اخبار مرتبط با آن برای شما ارسال خواهد شد.\n''' % Emoji.GLOWING_STAR
    # for entity in (related_entities.sort(key=lambda e: e.followers, reverse=True)):
    for entity in related_entities:
        text += tasks.prepare_advice_entity_link(entity) + '\n'
    return text


def send_related_entities(bot, msg, user, related_entities):
    send_telegram(bot, msg, user, show_related_entities(related_entities))
