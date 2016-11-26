import math
import re
import sys

from django.conf import settings
from telegram import InlineKeyboardMarkup
from telegram.inlinekeyboardbutton import InlineKeyboardButton

from entities import tasks
from entities.tasks import get_user_entity
from newsbot.global_settings import NEWS_PER_PAGE, DAYS_FOR_SEARCH_NEWS, SAMPLE_NEWS_COUNT
from rss import elastic
from rss.elastic import elastic_search_entity, similar_news_to_query
from rss.models import News
from rss.news import set_news_like
from telegrambot import news_template
from telegrambot.bot_send import send_telegram_user, error_text, send_telegram_chat
from telegrambot.models import UserNews, MessageFromUser, UserNewsList, UserSearchList
from telegrambot.models import UserProfile
from telegrambot.news_template import prepare_multiple_sample_news
from telegrambot.text_handler import search_box_result


def handle(bot, update):
    p = re.compile(r'[a-z]+')
    func = p.findall(update.callback_query.data.lower())[0] + '_inline_command'
    thismodule = sys.modules[__name__]
    if hasattr(thismodule, func):
        getattr(thismodule, func)(bot, update)
    else:
        error_text(bot, update, update.callback_query.from_user.up.user, error_type='NoCommand')


def news_inline_command(bot, update):
    d = re.compile(r'\d+').findall(update.callback_query.data.lower())
    news_id = d[0]
    user = update.callback_query.from_user.up.user
    news = News.objects.get(id=news_id)
    p = re.compile(r'[a-z]+')
    title = p.findall(update.callback_query.data.lower())[1]
    page = UserNews.objects.filter(news=news, user=user)[0].page
    picture_n = int(d[1])

    if title == 'like':
        set_news_like(user, news, mark='Like')
        ttt = 'پسندش شما ثبت شد!'
    elif title == 'unlike':
        set_news_like(user, news, mark='Unlike')
        ttt = 'پسندش شما پس گرفته شد!'
    elif title == 'overview':
        page = 1
        ttt = 'خلاصه‌ی خبر'
    elif title == 'full':
        page = 2
        ttt = 'متن کامل خبر'
    elif title == 'stat':
        page = 3
        ttt = 'اخبار مرتبط'
    elif title == 'img':
        ttt = 'عکس بعدی'
        picture_n += 1
        if picture_n > news.pic_number - 1:
            picture_n = 0
            ttt = 'عکس اول'
    else:
        ttt = 'دستور نامشخص'

    text = news_template.news_page(news,
                                   page=page,
                                   picture_number=picture_n,
                                   user_entity=tasks.get_user_entity(update.callback_query.from_user.up.user))
    keyboard = news_template.news_keyboard(news, update.callback_query.from_user.up.user, page,
                                           picture_number=picture_n)
    UserNews.objects.update_or_create(user=user, news=news, defaults={'page': page, 'image_page': picture_n})
    print(update.callback_query.message.chat)
    send_telegram_chat(bot, update.callback_query.message.chat.id, text,
                       keyboard=keyboard,
                       message_id=update.callback_query.message.message_id)
    bot.answerCallbackQuery(update.callback_query.id, text=ttt)


def continue_inline_command(bot, update):
    user = update.callback_query.from_user.up.user

    data_container = update.callback_query.data.split('continue-')[1].partition('-')[2].partition('-')
    news_id_list = []
    page_number = int(data_container[0])
    data_container_2 = data_container[2].partition('-')
    elastic_query = data_container_2[0]
    msg_id = data_container_2[2]

    try:
        query_text = MessageFromUser.objects.get(message_id=msg_id, type=1,
                                                 chat_id=update.callback_query.message.chat_id).message
    except MessageFromUser.DoesNotExist:
        bot.answerCallbackQuery(update.callback_query.id, text='خطا')
        return
    if page_number != 0:
        offset = page_number * NEWS_PER_PAGE - (NEWS_PER_PAGE - SAMPLE_NEWS_COUNT)

        if elastic_query == '0':
            hits = elastic_search_entity(query_text, NEWS_PER_PAGE, offset)
            news_id_list = list(map(int, [hit['_id'] for hit in hits]))

        elif elastic_query == '1':
            news_id_list = similar_news_to_query(query_text, NEWS_PER_PAGE, DAYS_FOR_SEARCH_NEWS, offset)

        if len(news_id_list) < NEWS_PER_PAGE:
            buttons = [[
                InlineKeyboardButton(text='صفحه قبل', callback_data='continue-' + 'previous-' + str(page_number - 1) +
                                                                    '-' + elastic_query + '-' + msg_id),
            ], ]
        else:
            buttons = [[
                InlineKeyboardButton(text='صفحه قبل', callback_data='continue-' + 'previous-' + str(page_number - 1) +
                                                                    '-' + elastic_query + '-' + msg_id),
                InlineKeyboardButton(text='صفحه بعد', callback_data='continue-' + 'next-' + str(page_number + 1) + '-' +
                                                                    elastic_query + '-' + msg_id),
            ], ]

        keyboard = InlineKeyboardMarkup(buttons)

        response = prepare_multiple_sample_news(news_id_list, NEWS_PER_PAGE)[0]

        send_telegram_user(bot, user, response, update, keyboard, update.callback_query.message.message_id)
    else:
        search_box_result(bot, update, user, msg_id, query_text)


def entitynewslist_inline_command(bot, msg):
    user = msg.callback_query.from_user.up.user

    unl = UserNewsList.objects.get(message_id=msg.callback_query.message.message_id)
    p = re.compile(r'[a-z]+')
    func = p.findall(msg.callback_query.data.lower())[1]

    if func == 'next':
        next_page = unl.page + 1
    else:
        next_page = unl.page - 1

    el_news = elastic.news_with_terms(entity_list=get_user_entity(user),
                                      size=settings.NEWS_PER_PAGE,
                                      start_time=unl.datetime_start,
                                      end_time=unl.datetime_publish,
                                      offset=(next_page - 1) * settings.NEWS_PER_PAGE
                                      )
    # start_time=up.user_settings.last_news_list.datetime_publish)
    if 1 < next_page < math.ceil(unl.number_of_news / settings.NEWS_PER_PAGE):
        buttons = [[
            InlineKeyboardButton(text='صفحه قبل', callback_data='entitynewslist-previous'),
            InlineKeyboardButton(text='صفحه بعد', callback_data='entitynewslist-next'),
        ], ]
    elif next_page == 1:
        buttons = [[
            InlineKeyboardButton(text='صفحه بعد', callback_data='entitynewslist-next'),
        ], ]
    else:
        buttons = [[
            InlineKeyboardButton(text='صفحه قبل', callback_data='entitynewslist-previous'),
        ], ]
    keyboard = InlineKeyboardMarkup(buttons)

    news_ent = [item['_id'] for item in el_news['hits']['hits']]
    news_list = list(set([item for item in news_ent]))
    output = 'اخبار مرتبط با دسته‌های شما'
    output += '\n'
    output += prepare_multiple_sample_news(news_list, settings.NEWS_PER_PAGE)[0]

    unl.page = next_page
    unl.save()

    send_telegram_user(bot, user, output, msg, keyboard, unl.message_id)


def searchlist_inline_command(bot, update):
    user = update.callback_query.from_user.up.user

    unl = UserSearchList.objects.get(message_id=update.callback_query.message.message_id)
    p = re.compile(r'[a-z]+')
    func = p.findall(update.callback_query.data.lower())[1]

    if func == 'next':
        next_page = unl.page + 1
    elif func == 'previous':
        next_page = unl.page - 1
    else:
        next_page = unl.page

    order = unl.order

    if func == 'time':
        order = 'N'
    elif func == 'rel':
        order = 'R'

    if order == 'N':
        sor = 'published_date'
        sort_key = InlineKeyboardButton(text='به ترتیب شباهت', callback_data='searchlist-rel')
    else:
        sor = '_score'
        sort_key = InlineKeyboardButton(text='به ترتیب زمان', callback_data='searchlist-time')

    similar_news = similar_news_to_query(query=unl.query,
                                         size=settings.NEWS_PER_PAGE,
                                         start_time=unl.datetime_start,
                                         end_time=unl.datetime_publish,
                                         offset=(next_page - 1) * settings.NEWS_PER_PAGE,
                                         sort=sor
                                         )

    # start_time=up.user_settings.last_news_list.datetime_publish)
    if 1 < next_page < math.ceil(unl.number_of_news / settings.NEWS_PER_PAGE):
        buttons = [[sort_key], [
            InlineKeyboardButton(text='صفحه قبل', callback_data='searchlist-previous'),
            InlineKeyboardButton(text='صفحه بعد', callback_data='searchlist-next'),
        ], ]
    elif next_page == 1:
        buttons = [[sort_key], [
            InlineKeyboardButton(text='صفحه بعد', callback_data='searchlist-next'),
        ], ]
    else:
        buttons = [[sort_key], [
            InlineKeyboardButton(text='صفحه قبل', callback_data='searchlist-previous'),
        ], ]
    keyboard = InlineKeyboardMarkup(buttons)

    news_ent = [item['_id'] for item in similar_news['hits']['hits']]
    news_list = news_ent
    output = prepare_multiple_sample_news(news_list, settings.NEWS_PER_PAGE)[0]

    unl.page = next_page
    unl.save()

    send_telegram_user(bot, user, output, update, keyboard, unl.message_id)


def interval_inline_command(bot, update):
    time_interval = int(update.callback_query.data.split('interval-')[1])
    user = update.callback_query.from_user.up.user
    user_setting = UserProfile.objects.get(user=user).user_settings
    last_interval = user_setting.interval_news_list

    if last_interval == time_interval:
        text = 'زمان انتخابی برابر با تنظیمات قبلی شماست.'
        send_telegram_user(bot, user, text, update)
    else:
        user_setting.interval_news_list = time_interval
        user_setting.save()
        text = 'تغییرات با موفقیت اعمال شد.\n'
        if time_interval < 60:
            time = time_interval
            time_type = 'دقیقه'
        else:
            time = int(time_interval / 60)
            time_type = 'ساعت'
        text += 'از این پس اخبار زنده هر %d %s برای شما ارسال می‌شود.' % (time, time_type)
        send_telegram_user(bot, user, text, update)
