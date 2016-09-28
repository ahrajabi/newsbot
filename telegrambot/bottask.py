import re
import telegram
from telegram.ext.dispatcher import run_async
from telegram.ext import MessageHandler, Filters, CallbackQueryHandler, Updater, Job, InlineQueryHandler
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, NetworkError)

from django.conf import settings
from telegrambot.publish import publish_handler
from telegrambot.bot_send import error_text
from telegrambot.models import MessageFromUser
from telegrambot import command_handler, news_template, callback, bot_send, inline


def error_callback(bot, update, error):
    print(":D:D:D::D:D:D::D:D:D::D:D:D")
    try:
        raise error
    except Unauthorized:
        print(update)
    except BadRequest:
        print("# handle malformed requests - read more below!")
    except TimedOut:
        print("# handle slow connection problems")
    except NetworkError:
        print("# handle other connection problems")
    except TelegramError:
        print("# handle all other telegram related errors")


@run_async
def handle(bot, msg):
    print(msg)
    bot.sendChatAction(chat_id=msg.message.chat_id, action=telegram.ChatAction.TYPING)
    user = command_handler.verify_user(bot, msg)[0]

    MessageFromUser.objects.create(user=user,
                                   message_id=msg.message.message_id,
                                   chat_id=msg.message.chat_id,
                                   type=1,
                                   message=msg.message.text)

    command_handler.handle(bot, msg, user)


@run_async
def commands(bot, msg):
    bot.sendChatAction(chat_id=msg.message.chat_id, action=telegram.ChatAction.TYPING)
    from telegrambot import command_handler, bot_template
    user, new_user = command_handler.verify_user(bot, msg)
    MessageFromUser.objects.create(user=user,
                                   message_id=msg.message.message_id,
                                   chat_id=msg.message.chat_id,
                                   type=2,
                                   message=msg.message.text)
    p = re.compile(r'[a-z]+')
    func = p.findall(msg.message.text.lower())[0] + '_command'
    if hasattr(command_handler, func):
        if func == 'start_command':
            getattr(command_handler, func)(bot, msg, new_user, user)
        else:
            getattr(command_handler, func)(bot, msg, user)
    else:
        error_text(bot, msg, user, type='NoCommand')


@run_async
def callback_query(bot, msg):
    callback.handle(bot, msg)


def user_alert_handler(bot, job):
    command_handler.user_alert_handler(bot, job)


def setup():
    updater = Updater(token=settings.TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler([Filters.command], commands))
    dispatcher.add_handler(MessageHandler([Filters.text], handle))
    dispatcher.add_handler(CallbackQueryHandler(callback_query))
    dispatcher.add_handler(InlineQueryHandler(inline.handler))
    dispatcher.add_error_handler(error_callback)

    q_bot = updater.job_queue
    q_bot.put(Job(publish_handler, 5, repeat=True))
    q_bot.put(Job(user_alert_handler, 100, repeat=True))
    if settings.DEBUG or True:
        updater.start_polling()
    else:
        updater.start_webhook(listen='130.185.76.171',
                              port='8443',
                              url_path=settings.TELEGRAM_TOKEN,
                              key='/etc/letsencrypt/live/soor.ir/privkey.pem',
                              cert='/etc/letsencrypt/live/soor.ir/fullchain.pem',
                              webhook_url='https://soor.ir:8443/'+settings.TELEGRAM_TOKEN)

    print('Listening ...')
