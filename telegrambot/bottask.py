# from telegram.ext.dispatcher import run_async
from telegram.ext import MessageHandler, Filters, CallbackQueryHandler, Updater, Job
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, NetworkError)

from django.conf import settings
from telegrambot.publish import publish_handler
from telegrambot.bot_send import error_text
from telegrambot import command_handler, callback, text_handler, wizard
from telegrambot.channel_publish import channel_publish_handler
from telegrambot.PreprocessHandler import PreprocessHandler
import re
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG)


def error_callback(bot, update, error):
    del bot, update
    try:
        raise error
    except Unauthorized:
        print("# remove update.message.chat_id from conversation list")
    except BadRequest:
        print("# handle malformed requests - read more below!")
    except TimedOut:
        print("# handle slow connection problems")
    except NetworkError:
        print("# handle other connection problems")
    except TelegramError:
        print("# handle all other telegram related errors")


def commands(bot, update):
    if hasattr(update, 'ignore'):
        return
    from telegrambot import command_handler
    p = re.compile(r'[a-z]+')
    func = p.findall(update.message.text.lower())[0] + '_command'
    if hasattr(command_handler, func):
        getattr(command_handler, func)(bot, update, update.message.chat.up.user)
    else:
        error_text(bot, update, update.message.chat.up.user, error_type='NoCommand')


def callback_query(bot, update):
    callback.handle(bot, update)


def user_alert_handler(bot, job):
    command_handler.user_alert_handler(bot, job)


def channel_publish(bot, job):
    channel_publish_handler(bot, job)


updater = Updater(token=settings.TELEGRAM_TOKEN)
dispatcher = updater.dispatcher

dispatcher.add_handler(wizard.SYMBOL_WIZARD, group=2)
dispatcher.add_handler(MessageHandler(Filters.command, commands), group=2)
dispatcher.add_handler(MessageHandler(Filters.text, text_handler.handle), group=2)
dispatcher.add_handler(CallbackQueryHandler(callback_query), group=2)
dispatcher.add_handler(PreprocessHandler(None), group=1)
dispatcher.add_error_handler(error_callback)

q_bot = updater.job_queue
q_bot.put(Job(publish_handler, 10, repeat=True))
q_bot.put(Job(user_alert_handler, 100, repeat=True))
q_bot.put(Job(channel_publish, 11, repeat=True))

if settings.DEBUG or True:
    updater.start_polling(bootstrap_retries=2)
else:
    updater.start_webhook(listen='146.185.154.208',
                          port='8443',
                          url_path=settings.TELEGRAM_TOKEN,
                          key='/etc/letsencrypt/live/khabareman.com/privkey.pem',
                          cert='/etc/letsencrypt/live/khabareman.com/fullchain.pem',
                          webhook_url='https://khabareman.com:8443/' + settings.TELEGRAM_TOKEN)

print('Listening ...')
