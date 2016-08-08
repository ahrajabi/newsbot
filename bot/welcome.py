from django.contrib.auth.models import User
from bot.models import UserProfile
from django.utils import timezone
from bot import bot_template
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from entities import tasks

def welcome_bot(bot, msg):
    user = User.objects.create_user(username=msg['from']['username'])

    up = user.userprofile_set.create(first_name=msg['from']['first_name'],last_name=msg['from']['last_name'],last_chat=timezone.now())

    print("NEW")
    keyboard , text = bot_template.welcome_text()
    bot.sendMessage(msg['from']['id'], text, reply_markup=keyboard)

def registered(bot, msg):
    return User.objects.filter(username=msg['from']['username'])


def getUser(bot, msg):
    return User.objects.get(username=msg['from']['username'])


def removeUser(bot, msg):
    if not registered(bot,msg):
        return
    u = User.objects.get(username=msg['from']['username'])
    u.delete()


def callback_query(bot,msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print(msg['data'])
    bot.answerCallbackQuery(query_id, text='Got it')


def handle(bot,user,msg):
    text = msg['text']
    if text.startswith('/'):
        if text.startswith('/add_'):
            entity_id = int(text[5:])
            if tasks.set_entity(user,entity_id , 'Active'):
                bot.sendMessage(msg['from']['id'], "DONE")
            else:
                keyboard, text = bot_template.error_text()
                bot.sendMessage(msg['from']['id'], text, reply_markup=keyboard)

        if text.startswith('/remove_'):
            entity_id = int(text[8:])
            if tasks.set_entity(user,entity_id , 'Deactive'):
                bot.sendMessage(msg['from']['id'], "DONE")
            else:
                keyboard, text = bot_template.error_text()
                bot.sendMessage(msg['from']['id'], text, reply_markup=keyboard)

    else:
        entity = tasks.get_entity(msg['text'])
        print(entity)
        if entity == None:
            keyboard, text = bot_template.error_text('NoEntity')
            bot.sendMessage(msg['from']['id'], text, reply_markup=keyboard)
        else:
            keyboard, text = bot_template.show_entities(entity)
            bot.sendMessage(msg['from']['id'], text, reply_markup=keyboard)


