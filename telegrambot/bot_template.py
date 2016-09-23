# -*- coding: utf-8 -*-
from telegram.emoji import Emoji
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from entities import tasks
from rss.models import ImageUrls
from rss.news import is_liked_news
from rss.elastic import more_like_this
from telegrambot.models import UserNews
from rss.ml import normalize, sent_tokenize
from entities.models import Entity, NewsEntity
from newsbot.settings import BOT_NAME, PROJECT_EN_NAME
from telegrambot.news_template import prepare_multiple_sample_news
from telegrambot.bot_send import send_telegram, send_telegram_user
from django.conf import settings

def welcome_text(bot, msg):
    keyboard = ReplyKeyboardMarkup(keyboard=[[
        '/HELP ⁉️ راهنمایی',
         ]], resize_keyboard=True)
    # TODO insert bot name in below text
    text = '''
        سلام  %s %s
        به بات خبری %s خوش آمدید.
🕴         اگر میخواهید اخبار مرتبط با شغل خود را ببیند (مثلا بورس)
🎻 یا خبرهای خواننده یا ورزشکار مورد علاقه خود را دنبال کنید (مثلا محسن چاوشی )
🏅 یا از اخبار پیرامون حادثه ای خاص مطلع شوید (مثلا المپیک)
 یا هر خبر دیگری

کلمه دلخواهتان را بنویسیدتا اخبار مرتبط با آن را ببینید و
اگر به موضوع علاقه مند هستید دسته های پیشنهادی را انتخاب کنید تا از این پس خبر های مرتبط به صورت برخط برای شما ارسال شود.

پس شروع کنید و کلمه مورد نظرتان را از طریق کادر پایین ارسال کنید %s

        ''' % (msg.message.from_user.first_name, Emoji.RAISED_HAND, PROJECT_EN_NAME,
               Emoji.WHITE_DOWN_POINTING_BACKHAND_INDEX)
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
    ]
    text = 'راهنما'+'\n'

    for i in menu:
        text += i[0] + ' ' + i[1] + '\n'
    send_telegram_user(bot, user, text, None)


def news_image_page(bot, news, user, page=1, message_id=None):
    keyboard = None
    image_url = ImageUrls.objects.filter(news=news)
    if image_url:
        image_url = image_url[0].img_url
    else:
        image_url = settings.TELEGRAM_LOGO


    UserNews.objects.update_or_create(user=user, news=news, defaults={'image_page': page})
    text = news.base_news.title
    send_telegram_user(bot, user, text, keyboard, message_id, photo=image_url)
    print(image_url)


def news_page(bot, news, user, page=1, message_id=None, **kwargs):
    like = InlineKeyboardButton(text=Emoji.THUMBS_UP_SIGN + "(" + normalize(str(news.like_count)) + ")",
                                callback_data='news-' + str(news.id) + '-like')

    if is_liked_news(news=news, user=user):
        like = InlineKeyboardButton(text=Emoji.THUMBS_DOWN_SIGN + "(" + normalize(str(news.like_count)) + ")",
                                    callback_data='news-' + str(news.id) + '-unlike')

    buttons = [
        [
            InlineKeyboardButton(text='خلاصه', callback_data='news-' + str(news.id) + '-overview'),
            InlineKeyboardButton(text='متن کامل خبر', callback_data='news-' + str(news.id) + '-full'),
         ],
        [
            InlineKeyboardButton(text='اخبار مرتبط', callback_data='news-' + str(news.id) + '-stat'),
            like,
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
        try:
            text += '\n' + Emoji.WHITE_HEAVY_CHECK_MARK + 'منبع:‌ ' + news.base_news.rss.news_agency.fa_name + '\n'
        except Exception:
            pass

        if 'user_entity' in kwargs:
            news_user_entity = NewsEntity.objects.filter(news=news, entity__in=kwargs['user_entity'])
            if news_user_entity:
                text += '\n' + Emoji.BOOKMARK + ' دسته های مشترک با علاقه مندی شما:\n'
                for en in news_user_entity:
                    text += en.entity.name + ', '
                text += '\n'

    elif page == 2:
        try:
            text += Emoji.PUBLIC_ADDRESS_LOUDSPEAKER + news.base_news.title + '\n\n    '
        except Exception:
            pass

        if len(news.body) < 3500:
            text += news.body + '\n'
        else:
            text += news.body[:3500].rsplit(' ', 1)[0]
            text += '\n' + 'ادامه دارد...' + '\n'
    elif page == 3:
        related = more_like_this(news.base_news.title, 5)
        text, notext = prepare_multiple_sample_news(related, 5)
    text += BOT_NAME

    send_telegram_user(bot, user, text, keyboard, message_id)
    UserNews.objects.update_or_create(user=user, news=news, defaults={'page': page})


def publish_news(bot, news, user, page=1, message_id=None, **kwargs):
    try:
        news_image_page(bot, news, user, page=1, message_id=message_id)
    except:
        pass
    news_page(bot, news, user, page, message_id=message_id, **kwargs)


def after_user_add_entity(bot, msg, user, entity, entities):
    text = "دسته ' %s ' اضافه شد %s" % (entity, Emoji.PUSHPIN)
    send_telegram(bot, msg, text)
    show_user_entity(bot, msg, user, entities)


def entity_recommendation():
    return Entity.objects.order_by('followers')[:5]


def prepare_advice_entity_link(entity):
    return Emoji.SMALL_ORANGE_DIAMOND + "/add_"+str(entity.id)+" " + entity.name + ""


def show_related_entities(related_entities):
    text = Emoji.HEAVY_MINUS_SIGN * 6 + Emoji.WHITE_LEFT_POINTING_BACKHAND_INDEX + " دسته های مرتبط " +\
           Emoji.WHITE_RIGHT_POINTING_BACKHAND_INDEX + Emoji.HEAVY_MINUS_SIGN * 6
    text += '''
     %s دسته های مرتبط با متن وارد شده در زیر آمده است.
    با انتخاب هرکدام، اخبار مرتبط با آن به صورت بر خط  برای شما ارسال خواهد شد.\n''' % Emoji.BOOKMARK
    # for entity in (related_entities.sort(key=lambda e: e.followers, reverse=True)):
    for entity in related_entities:
        text += prepare_advice_entity_link(entity) + '\n'
    return text


def send_related_entities(bot, msg, user, related_entities):
    send_telegram(bot, msg, user, show_related_entities(related_entities))


def one_entity_recommendation(entity):
    text = ""
    text += Emoji.WHITE_DOWN_POINTING_BACKHAND_INDEX + '\n'
    text += prepare_advice_entity_link(entity)
    return text
