from django.conf import settings
from telegram.ext import Updater, Job
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import telegram
import re
import logging
from django.contrib.auth.models import User
from newsbot import local_settings
from telegram.ext.dispatcher import run_async
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, NetworkError)
from telegrambot import command_handler, bot_template, callback
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


TOKEN = local_settings.TELEBOT_TOKEN  # get token from command-line


@run_async
def handle(bot, msg):
    print(msg)
    bot.sendChatAction(chat_id=msg.message.chat_id, action=telegram.ChatAction.TYPING)
    user = command_handler.verify_user(bot, msg)[0]

    command_handler.handle(bot, msg, user)


@run_async
def commands(bot, msg):
    bot.sendChatAction(chat_id=msg.message.chat_id, action=telegram.ChatAction.TYPING)
    from telegrambot import command_handler, bot_template
    user, new_user = command_handler.verify_user(bot, msg)

    p = re.compile(r'[a-z]+')
    func = p.findall(msg.message.text.lower())[0] + '_command'
    if hasattr(command_handler, func):
        if func == 'start_command':
            getattr(command_handler, func)(bot, msg, new_user)
        else:
            getattr(command_handler, func)(bot, msg, user)
    else:
        bot_template.error_text(bot, msg, type='NoCommand')


@run_async
def callback_query(bot, msg):
    callback.handle(bot, msg)


def user_alert_handler(bot,job):
    command_handler.user_alert_handler(bot,job)


def fetch_news(bot, job):
    # bulk_save_to_elastic()
    # news.postgres_news_to_elastic()
    # rss.get_new_rss()
    # news.save_all_base_news()
    pass


def random_publish_news(bot, job):
    from rss.models import News
    news = News.objects.filter(pic_number__gte=1,
                               summary__isnull=False).order_by('?')
    user = User.objects.all()[0]
    bot_template.publish_news(bot, news[0], user )

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler([Filters.command], commands))
dispatcher.add_handler(MessageHandler([Filters.text], handle))
dispatcher.add_handler(CallbackQueryHandler(callback_query))
dispatcher.add_error_handler(error_callback)

q_bot = updater.job_queue

# q_bot.put(Job(random_publish_news, 10, repeat=True))
q_bot.put(Job(user_alert_handler, 100, repeat=True))
q_bot.put(Job(fetch_news, 2, repeat=True))

updater.start_polling()
print('Listening ...')
