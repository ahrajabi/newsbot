from django.conf import settings
from telegram.ext import Updater, Job
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import telegram
import re
import logging
from django.contrib.auth.models import User

from telegram.ext.dispatcher import run_async
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, NetworkError)
from telegrambot import welcome, bot_template, callback
from telegrambot.models import UserProfile
from rss import rss,news
from rss.elastic import bulk_save_to_elastic
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        print("remove update.message.chat_id from conversation list")
    except BadRequest:
        print("# handle malformed requests - read more below!")
    except TimedOut:
        print("# handle slow connection problems")
    except NetworkError:
        print("# handle other connection problems")
    # except ChatMigrated as e:
    #    print("# the chat_id of a group has changed, use e.new_chat_id instead")
    except TelegramError:
        print("# handle all other telegram related errors")


TOKEN = settings.TELEBOT_TOKEN  # get token from command-line


@run_async
def handle(bot, msg):
    bot.sendChatAction(chat_id=msg.message.chat_id, action=telegram.ChatAction.TYPING)
    user = welcome.verifyUser(bot, msg)
    welcome.handle(bot, msg, user)


@run_async
def commands(bot, msg):
    bot.sendChatAction(chat_id=msg.message.chat_id, action=telegram.ChatAction.TYPING)
    from telegrambot import welcome, bot_template
    user = welcome.verifyUser(bot, msg)

    p = re.compile(r'[a-z]+')
    func = p.findall(msg.message.text.lower())[0] + '_command'
    if hasattr(welcome, func):
        getattr(welcome, func)(bot, msg, user)
    else:
        bot_template.error_text(bot, msg, type='NoCommand')


@run_async
def callback_query(bot, msg):

    callback.handle(bot, msg)

def user_alert_handler(bot,job):
    welcome.user_alert_handler(bot,job)

def fetch_news(bot, job):
    news.postgres_news_to_elastic()
    rss.get_new_rss()
    news.save_all_base_news()

def random_publish_news(bot,job):
    from rss.models import News
    news = News.objects.filter(pic_number__gte=1,
                               summary__isnull=False).order_by('?')
    user = User.objects.get(username='ahrajabi')
    bot_template.publish_news(bot, news[0], user )

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler([Filters.command], commands))
dispatcher.add_handler(MessageHandler([Filters.text], handle))
dispatcher.add_handler(CallbackQueryHandler(callback_query))
dispatcher.add_error_handler(error_callback)

q_bot = updater.job_queue

q_bot.put(Job(random_publish_news, 60*60, repeat=True))
q_bot.put(Job(user_alert_handler, 100, repeat=True))
q_bot.put(Job(fetch_news, 20, repeat=True))

updater.start_polling()
print('Listening ...')
