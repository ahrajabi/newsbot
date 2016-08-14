
from telegrambot.models import UserProfile
from django.utils import timezone
from telegrambot import bot_template , welcome
from entities import tasks
import re
import sys
from newsbot.celery import app
thismodule = sys.modules[__name__]
import pprint
import telegram

def handle(bot,msg):
    user = welcome.getUser(msg.callback_query.message.chat.id)
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