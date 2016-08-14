import telepot
from telegrambot import token
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import telegram
import re
import logging
from telegram.ext.dispatcher import run_async
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, NetworkError)

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
    #except ChatMigrated as e:
    #    print("# the chat_id of a group has changed, use e.new_chat_id instead")
    except TelegramError:
        print("# handle all other telegram related errors")



TOKEN = token.TELEBOT_TOKEN  # get token from command-line

@run_async
def handle(bot, msg):
    bot.sendChatAction(chat_id=msg.message.chat_id, action=telegram.ChatAction.TYPING)
    from telegrambot import welcome

    from telegrambot.models import UserProfile

    user = welcome.verifyUser(bot, msg)
    welcome.handle(bot,msg)


@run_async
def commands(bot, msg):
    print(msg)
    bot.sendChatAction(chat_id=msg.message.chat_id, action=telegram.ChatAction.TYPING)
    from telegrambot import welcome, bot_template
    user = welcome.verifyUser(bot, msg)

    p = re.compile(r'[a-z]+')
    func = p.findall(msg.message.text.lower())[0] + '_command'
    print(func)
    if hasattr( welcome ,func):
        getattr( welcome , func)(bot, msg,user)
    else:
        bot_template.error_text(bot, msg, type = 'NoCommand')

@run_async
def callback_query(bot,msg):
    from telegrambot import callback

    callback.handle(bot,msg)


def asdf(bot,update):
    print("hello")

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler([Filters.command], commands))
dispatcher.add_handler(MessageHandler([Filters.text], handle))
dispatcher.add_handler( CallbackQueryHandler(callback_query) )
dispatcher.add_error_handler(error_callback)
updater.start_polling()
print ('Listening ...')