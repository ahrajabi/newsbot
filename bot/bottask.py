import telepot
from bot import token
TOKEN = token.TELEBOT_TOKEN  # get token from command-line

def handle(msg):
    from bot import welcome
    if 'data' in msg:
        welcome.callback_query(bot,msg)
        return
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(msg)

    # Remove User for Testing
    #welcome.removeUser(bot,msg)
    from bot.models import UserProfile

    userid = msg['from']['id']

    if not welcome.registered(bot, msg) :
        welcome.welcome_bot(bot, msg)
        return

    user = welcome.getUser(bot, msg)
    if content_type == 'text':
        welcome.handle(bot,user, msg)


bot = telepot.Bot(TOKEN)
bot.message_loop({'chat':handle , 'callback_query':handle})
print ('Listening ...')


