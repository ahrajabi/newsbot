import telepot
import bot.token
TOKEN = bot.token.TELEBOT_TOKEN  # get token from command-line

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'text':
        bot.sendMessage(chat_id, msg['text'])


bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print ('Listening ...')
