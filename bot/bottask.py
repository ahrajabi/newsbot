from celery.decorators import task
from django.conf import settings
import time
import telepot


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'text':
        bot.sendMessage(chat_id, msg['text']+"hesss")


TOKEN = settings.TELEBOT_TOKEN  # get token from command-line
bot = telepot.Bot(TOKEN)

print(bot)

bot.message_loop(handle)
print ('Listening ...')




@task()
def bot_start():
	while 1:
		print("0000")
		time.sleep(10)


print("HHH")
#bot_start.delay()

