
import re
import sys
from telegram import InlineKeyboardMarkup
from telegram.inlinekeyboardbutton import InlineKeyboardButton
import math
from entities import tasks
from rss.models import News
from rss.news import set_news_like
from telegrambot import command_handler, news_template
from telegrambot.command_handler import search_box_result
from telegrambot.bot_send import send_telegram_user, error_text
from telegrambot.news_template import prepare_multiple_sample_news
from telegrambot.models import UserNews, MessageFromUser, UserNewsList
from rss.elastic import elastic_search_entity, similar_news_to_query
from newsbot.global_settings import NEWS_PER_PAGE, DAYS_FOR_SEARCH_NEWS, SAMPLE_NEWS_COUNT
from django.conf import settings
from rss import elastic
from entities.tasks import get_user_entity
thismodule = sys.modules[__name__]


def handle(bot, msg):
    user = command_handler.get_user(msg.callback_query.message.chat.id)
    p = re.compile(r'[a-z]+')
    func = p.findall(msg.callback_query.data.lower())[0] + '_inline_command'
    print(func)
    MessageFromUser.objects.create(user=user,
                                   message_id=msg.callback_query.message.message_id,
                                   chat_id=msg.callback_query.message.chat_id,
                                   type=3,
                                   message=msg.callback_query.data)
    if hasattr(thismodule, func):
        getattr(thismodule, func)(bot, msg, user)
    else:
        error_text(bot, msg, type='NoCommand')


def score_inline_command(bot, msg, user):
    entity_id = re.compile(r'\d+').findall(msg.callback_query.data.lower())[0]
    score = re.compile(r'\(((-|)\d*?)\)').findall(msg.callback_query.data.lower())[0][0]
    if tasks.set_score_entity(user, entity_id, int(score)):
        TEXT = '''
علاقه شما به اخبار  %s با مقدار %d تنظیم شد.
        ''' % (tasks.get_entity(entity_id).name, int(score)+3)
        print(msg)
        bot.answerCallbackQuery(msg.callback_query.id,
                                text=TEXT)
    else:
        error_text(bot, msg)


def news_inline_command(bot, msg, user):
    news_id = re.compile(r'\d+').findall(msg.callback_query.data.lower())[0]
    news = News.objects.get(id=news_id)
    p = re.compile(r'[a-z]+')
    title = p.findall(msg.callback_query.data.lower())[1]
    page = UserNews.objects.filter(news=news, user=user)[0].page

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

    news_template.news_page(bot, news, user,
                           page=page, message_id=msg.callback_query.message.message_id,
                           user_entity=tasks.get_user_entity(user))

    bot.answerCallbackQuery(msg.callback_query.id, text=ttt)


def continue_inline_command(bot, msg, user):
    # elastic_query == 0 --> elastic_search_entity
    # elastic_query == 1 --> similar_news_to_query

    data_container = msg.callback_query.data.split('continue-')[1].partition('-')[2].partition('-')
    news_id_list = []
    page_number = int(data_container[0])
    data_container_2 = data_container[2].partition('-')
    elastic_query = data_container_2[0]
    msg_id = data_container_2[2]

    try:
        query_text = MessageFromUser.objects.get(message_id=msg_id, type=1,
                                                 chat_id=msg.callback_query.message.chat_id).message
    except MessageFromUser.DoesNotExist:
        bot.answerCallbackQuery(msg.callback_query.id, text='خطا')
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

        send_telegram_user(bot, user, response, keyboard, msg.callback_query.message.message_id)
    else:
        search_box_result(bot, msg, user, msg_id, query_text)


def entitynewslist_inline_command(bot, msg, user):
    import logging
    logging.config.dictConfig(settings.LOGGING)

    unl = UserNewsList.objects.get(message_id=msg.callback_query.message.message_id)
    p = re.compile(r'[a-z]+')
    func = p.findall(msg.callback_query.data.lower())[1]

    if func == 'next':
        next_page = unl.page+1
    elif func == 'previous':
        next_page = unl.page-1

    print(func, next_page)

    ent = get_user_entity(user)
    el_news = elastic.news_with_terms(terms_list=[item.name for item in ent],
                                      size=settings.NEWS_PER_PAGE,
                                      start_time=unl.datetime_start,
                                      end_time=unl.datetime_publish,
                                      offset=(next_page-1)*settings.NEWS_PER_PAGE
                                      )
    print(el_news)
    # start_time=up.user_settings.last_news_list.datetime_publish)
    print(math.ceil(unl.number_of_news/settings.NEWS_PER_PAGE))
    if next_page > 1 and next_page < math.ceil(unl.number_of_news/settings.NEWS_PER_PAGE):
        buttons = [[
            InlineKeyboardButton(text='صفحه بعد', callback_data='entitynewslist-next'),
            InlineKeyboardButton(text='صفحه قبل', callback_data='entitynewslist-previous'),
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
    print(news_list)
    output += prepare_multiple_sample_news(news_list, settings.NEWS_PER_PAGE)[0]

    unl.page= next_page
    unl.save()

    send_telegram_user(bot, user, output, keyboard, unl.message_id)