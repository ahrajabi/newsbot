import telepot
from bot import token
TOKEN = token.TELEBOT_TOKEN  # get token from command-line




def handle(msg):
    from bot import welcome
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    print(msg)

    # Remove User
    welcome.removeUser(msg)


    userid = msg['from']['id']
    if welcome.registered(bot,msg) :
        print("REGISTERED")
    if not welcome.registered(bot, msg) :
        welcome.welcome_bot(bot, msg)
        return

    user = welcome.getUser(bot, msg)
    if content_type == 'text':
        bot.sendMessage(chat_id, "salam</b>")


bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print ('Listening ...')
