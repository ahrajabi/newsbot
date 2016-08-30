
from telegrambot.models import UserProfile
from django.utils import timezone
from telegrambot import bot_template , command_handler
from entities import tasks
import re
import sys
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



def score_inline_command(bot, msg,user):
    entity_id = re.compile(r'\d+').findall(msg.callback_query.data.lower())[0]
    Score = re.compile(r'\(((-|)\d*?)\)').findall(msg.callback_query.data.lower())[0][0]
    if tasks.set_score_entity(user,entity_id,int(Score)):
        TEXT = '''
علاقه شما به اخبار  %s با مقدار %d تنظیم شد.
        ''' % ( tasks.get_entity(entity_id).name ,int(Score)+3)
        print(msg)
        bot.answerCallbackQuery(msg.callback_query.id,
                                text=TEXT)
    else:
        bot_template.error_text(bot, msg)


def news_inline_command(bot,msg,user):
    news_id = re.compile(r'\d+').findall(msg.callback_query.data.lower())[0]
    bot.answerCallbackQuery(msg.callback_query.id,
                            text='news')
    from rss.models import News

    p = re.compile(r'[a-z]+')
    pageTitle = p.findall(msg.callback_query.data.lower())[1]

    Page = 1

    if pageTitle == 'overview':
        Page = 1
    elif pageTitle == 'full':
        Page = 2
    elif pageTitle == 'stat':
        Page = 3

    News = News.objects.get(id=news_id)
    user = UserProfile.objects.get(telegram_id=msg.callback_query.message.chat.id).user
    bot_template.publish_news(bot, News, user,
                 page=Page, message_id=msg.callback_query.message.message_id)



