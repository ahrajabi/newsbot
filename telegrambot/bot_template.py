# -*- coding: utf-8 -*-
import telegram
from entities import tasks
from rss.ml import normalize
from telegram.emoji import Emoji
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from rss.models import ImageUrls
from rss.news import is_liked_news

from entities import tasks
from rss.models import News
from entities.models import Entity
from rss.ml import sent_tokenize
from telegrambot.models import UserProfile, UserNews

from rss.elastic import more_like_this

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


def error_text(bot, msg, type=None):
    text = 'ERROR'
    if type == 'NoEntity':
        text = '''        دسته مورد نظر موجود نمی‌باشد.'''

    elif type == 'LongMessage':
        text = '''
        نتیجه درخواست شما بسیار طولانی است.
        و امکان ارسال آن وجود ندارد.
        '''

    elif type == 'NoCommand':
        text = '''
         چنین دستوری تعریف نشده است %s
⁉️ راهنمایی را ببینید
        ''' % Emoji.WARNING_SIGN

    elif type == 'PriorFollow':
        text = '''
        شما قبلا این دسته را اضافه کرده اید!
        '''
    elif type == 'NoFallow':
        text = '''
        شما این دسته را دنبال نمی کرده اید.
        '''
    elif type == 'InvalidEntity':
        text = ''' دسته وارد شده مورد قبول نیست %s ''' % Emoji.NO_ENTRY_SIGN

    elif type == 'RepetitiveStart':
        text = '''شما قبلا وارد شده ایدبرای استفاده بهتر
⁉️ راهنمایی را ببینید
'''

    elif type == 'NoneNews':
        text = "خبر مورد نظر موجود نمی باشد!"
    return send_telegram(bot, msg, text, None)


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
    # keyboard = None
    # if news.pic_number > 1:
    #     if page>1 and page<news.pic_number:
    #         buttons = [[
    #             InlineKeyboardButton(text='تصویر قبلی', callback_data='image-' + str(news.id) + '-previous'),
    #             InlineKeyboardButton(text='تصویر بعدی', callback_data='image-' + str(news.id) + '-next'),
    #         ]]
    #     elif page == 0:
    #         buttons = [[
    #             InlineKeyboardButton(text='تصویر بعدی', callback_data='image-' + str(news.id) + '-next'),
    #         ]]
    #     elif page == news.pic_number:
    #         buttons = [[
    #             InlineKeyboardButton(text='تصویر قبلی', callback_data='image-' + str(news.id) + '-previous'),
    #             InlineKeyboardButton(text='تصویر بعدی', callback_data='image-' + str(news.id) + '-next'),
    #         ]]
    #     keyboard = InlineKeyboardMarkup(buttons)

    keyboard = None
    image_url = ImageUrls.objects.filter(news=news)
    if not image_url:
        return
    image_url = image_url[0].img_url
    UserNews.objects.update_or_create(user=user, news=news, defaults={'image_page': page})
    text = news.base_news.title
    send_telegram_user(bot, user, text, keyboard, message_id, photo=image_url)


def news_page(bot, news, user, page=1, message_id=None):
    like = InlineKeyboardButton(text=Emoji.THUMBS_UP_SIGN + "(" + normalize(str(news.like_count)) + ")",
                                callback_data='news-' + str(news.id) + '-like')

    if is_liked_news(news=news,user=user):
        like = InlineKeyboardButton(text=Emoji.THUMBS_DOWN_SIGN + "(" + normalize(str(news.like_count)) + ")",
                                    callback_data='news-' + str(news.id) + '-unlike')

    buttons = [[like, ],
        [
            InlineKeyboardButton(text='خلاصه', callback_data='news-' + str(news.id) + '-overview'),
            InlineKeyboardButton(text='متن کامل خبر', callback_data='news-' + str(news.id) + '-full'),
            InlineKeyboardButton(text='تحلیل', callback_data='news-' + str(news.id) + '-stat'),
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

    elif page == 2:
        text += news.body[0:1000] + '\n' + 'ادامه دارد' + '\n'
    elif page == 3:
        related = more_like_this(news.base_news.title, 5)
        for item in related:
            try:
                text += sample_news_page(News.objects.get(id=item))
            except:
                pass
        text += '----------------\n'
        text += 'منبع خبر' + news.base_news.rss.fa_name + '\n'
        text += 'تاریخ ارسال' + str(news.base_news.published_date) + '\n'


    text += '@mybot بات من'

    send_telegram_user(bot, user, text, keyboard, message_id)
    UserNews.objects.update_or_create(user=user, news=news, defaults={'page': page})


def publish_news(bot, news, user, page=1, message_id=None):
    news_image_page(bot, news, user, page=1, message_id=None)
    news_page(bot, news, user, page, message_id=None)


def send_telegram(bot, msg, text, keyboard=None):
    if len(text) > 4096:
        error_text(msg, type="LongMessage")
        return False
    return bot.sendMessage(chat_id=msg.message.chat_id,
                           text=text,
                           reply_markup=keyboard,
                           parse_mode=telegram.ParseMode.HTML)


def send_telegram_user(bot, user, text, keyboard=None, message_id=None, photo=None):
    profile = UserProfile.objects.get(user=user)
    p_id = profile.telegram_id

    if p_id:
        if photo==None:
            if not message_id:
                return bot.sendMessage(chat_id=p_id,
                                       text=text,
                                       reply_markup=keyboard,
                                       parse_mode=telegram.ParseMode.HTML)
            else:
                bot.editMessageText(text=text,
                                    chat_id=p_id,
                                    message_id=message_id,
                                    reply_markup=keyboard,
                                    parse_mode=telegram.ParseMode.HTML,
                                    inline_message_id=None)
        else:
            bot.sendPhoto(chat_id=p_id,
                          photo=photo,
                          caption=text[0:199],
                          reply_markup=keyboard,
                          parse_mode=telegram.ParseMode.HTML)


def send_telegram_all_user(bot, text, keyboard=None, photo=None):
    all_profile = UserProfile.objects.all()
    for profile in all_profile:
        id = profile.telegram_id
        if id:
            if photo:
                bot.sendPhoto(chat_id=id,
                              photo=photo,
                              caption=text[0:199],
                              reply_markup=keyboard,
                              parse_mode=telegram.ParseMode.HTML)
            else:
                bot.sendMessage(chat_id=id,
                                text=text,
                                reply_markup=keyboard,
                                parse_mode=telegram.ParseMode.HTML)


def after_user_add_entity(bot, msg, user, entity, entities):
    text = "دسته ' %s ' اضافه شد %s" % (entity, Emoji.PUSHPIN)
    send_telegram(bot, msg, text)
    show_user_entity(bot, msg, user, entities)


def entity_recommendation():
    return Entity.objects.order_by('followers')[:5]


def show_related_entities(bot, msg, user, related_entities):
    text = ''' %s دسته های مرتبط با متن وارد شده در زیر آمده است
    با انتخاب هرکدام اخبار مرتبط با آن برای شما ارسال خواهد شد\n''' %Emoji.DIAMOND_SHAPE_WITH_A_DOT_INSIDE
    # for entity in (related_entities.sort(key=lambda e: e.followers, reverse=True)):
    for entity in related_entities:
        text += tasks.prepare_advice_entity_link(entity) + '\n'

    send_telegram(bot, msg, text)


def sample_news_page(news):
    title = news.base_news.title
    source = news.base_news.rss.fa_name
    text = Emoji.SMALL_BLUE_DIAMOND + title + '\n' + source + '\t\t\t/News_' + str(news.id) + '\n'
    return text


def publish_sample_news(bot, user, msg, news_id_list):
    news_count = 0
    text = "%s خبرهای مرتبط:\n" % Emoji.NEWSPAPER
    for news_id in news_id_list:
        try:
            text += sample_news_page(News.objects.get(id=news_id))
            if news_count > 4:
                break
        except News.DoesNotExist:
            continue
    send_telegram(bot, msg, text)
