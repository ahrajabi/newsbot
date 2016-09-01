
from telegrambot.models import UserProfile, UserNews
from django.utils import timezone
from telegrambot import bot_template , command_handler
from entities import tasks
import re
import sys
from rss.models import News
from rss.news import set_news_like
from telegram.emoji import Emoji

from newsbot.celery import app
from django.contrib.auth.models import User

thismodule = sys.modules[__name__]
import pprint
import telegram


def handle(bot,msg):
    user = command_handler.get_user(msg.callback_query.message.chat.id)
    p = re.compile(r'[a-z]+')
    func = p.findall(msg.callback_query.data.lower())[0] + '_inline_command'
    print(func)
    if hasattr(thismodule, func):
        getattr(thismodule, func)(bot, msg, user)
    else:
        bot_template.error_text(bot, msg, type='NoCommand')


def score_inline_command(bot, msg, user):
    entity_id = re.compile(r'\d+').findall(msg.callback_query.data.lower())[0]
    score = re.compile(r'\(((-|)\d*?)\)').findall(msg.callback_query.data.lower())[0][0]
    if tasks.set_score_entity(user,entity_id,int(score)):
        TEXT = '''
علاقه شما به اخبار  %s با مقدار %d تنظیم شد.
        ''' % (tasks.get_entity(entity_id).name, int(score)+3)
        print(msg)
        bot.answerCallbackQuery(msg.callback_query.id,
                                text=TEXT)
    else:
        bot_template.error_text(bot, msg)


def news_inline_command(bot, msg, user):
    news_id = re.compile(r'\d+').findall(msg.callback_query.data.lower())[0]
    news = News.objects.get(id=news_id)
    p = re.compile(r'[a-z]+')
    title = p.findall(msg.callback_query.data.lower())[1]
    page = UserNews.objects.filter(news=news, user=user)[0].page

    if title == 'like':
        set_news_like(user,news,mark='Like')
        bot.answerCallbackQuery(msg.callback_query.id, text='پسندش شما ثبت شد!')
    elif title == 'unlike':
        set_news_like(user, news, mark='Unlike')
        bot.answerCallbackQuery(msg.callback_query.id, text='پسندش شما پس گرفته شد!')
    elif title == 'overview':
        page = 1
        bot.answerCallbackQuery(msg.callback_query.id, text='خلاصه‌ی خبر')
    elif title == 'full':
        page = 2
        bot.answerCallbackQuery(msg.callback_query.id, text='متن کامل خبر')
    elif title == 'stat':
        page = 3
        bot.answerCallbackQuery(msg.callback_query.id, text='تحلیل خبر')
    bot_template.news_page(bot, news, user,
                           page=page, message_id=msg.callback_query.message.message_id)



