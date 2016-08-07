from django.contrib.auth.models import User


def welcome_bot(bot, msg):
    user = User.objects.create_user(username=msg['from']['id'])
    print("NEW")
    welcome_text = '''
    برای شروع لطفا بر روی موضوع های مورد علاقه‌یتان کلیک کنید. در آینده به راحتی می توانید موضوعات را اضافه ویا حذف نمایید.
    %s
    %s
    ''' % ('salam','/start')
    bot.sendMessage(msg['from']['id'], welcome_text)

def registered(bot, msg):
    return User.objects.filter(username=msg['from']['id'])


def getUser(bot, msg):
    return User.objects.get(username=msg['from']['id'])


def removeUser(msg):
    u = User.objects.get(username=msg['from']['id'])
    u.delete()