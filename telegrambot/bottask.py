import re
import logging
import telegram
from datetime import timedelta
from django.utils import timezone
from telegram.ext.dispatcher import run_async
from django.contrib.auth.models import User
from telegram.ext import MessageHandler, Filters, CallbackQueryHandler, Updater, Job
from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut, NetworkError

from rss import tasks
from newsbot import local_settings
from entities.models import NewsEntity
from entities.tasks import get_user_entity
from telegrambot.bot_send import error_text
from telegrambot import command_handler, news_template, callback, bot_send

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
        error_text(bot, msg, type='NoCommand')


@run_async
def callback_query(bot, msg):
    callback.handle(bot, msg)


def user_alert_handler(bot, job):
    command_handler.user_alert_handler(bot, job)


def crawler(bot, job):
    print("RUN")
    tasks.get_all_new_news.delay()
    tasks.bulk_save_to_elastic.delay()
    tasks.save_all_base_news.delay()

def random_publish_news(bot,job):
    print("BOBO")
    delta = timezone.now()-timedelta(minutes=10)
    for user in User.objects.all():
        ent = get_user_entity(user)
        news_ent = NewsEntity.objects.filter(entity__in=ent, )\
            .order_by('news__base_news__published_date')
        print(user.username, news_ent.count())
        news_list = set([item.news_id for item in news_ent])
        output = news_template.prepare_multiple_sample_news(list(news_list), 20)
        bot_send.send_telegram_user(bot, user, output[0])


updater = Updater(token=TOKEN)

dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler([Filters.command], commands))
dispatcher.add_handler(MessageHandler([Filters.text], handle))
dispatcher.add_handler(CallbackQueryHandler(callback_query))
dispatcher.add_error_handler(error_callback)

q_bot = updater.job_queue

q_bot.put(Job(random_publish_news, 10*60, repeat=True))
q_bot.put(Job(user_alert_handler, 100, repeat=True))

q_bot.put(Job(crawler, 30, repeat=True))

updater.start_polling()
print('Listening ...')
