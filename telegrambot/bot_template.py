import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup
from entities import tasks
from django.contrib.auth.models import User
from telegrambot.models import UserProfile
def welcome_text(bot, msg):
    keyboard = ReplyKeyboardMarkup(keyboard=[[
        '/HELP ⁉️ راهنمایی',
         ]],resize_keyboard=True)

    WELCOME_TEXT = '''
    برای شروع لطفا بر روی موضوع های مورد علاقه‌یتان کلیک کنید. در آینده به راحتی می توانید موضوعات را اضافه ویا حذف نمایید.
    %s
    %s
    '''
    return send_telegram(bot, msg, WELCOME_TEXT, keyboard)


def show_entities(bot, msg,user, entities):
    keyboard = None
    text = ''
    button = list()
    for item in entities:
        text += tasks.get_link(user,item) + '\n'
    #    button.append([InlineKeyboardButton(text=item.name, callback_data="data")])
    #keyboard = InlineKeyboardMarkup(inline_keyboard=button)
    return send_telegram(bot, msg, text, keyboard)

def show_user_entity(bot, msg, user , entities):
    TEXT = ''
    if entities:
        TEXT = 'شما در دسته های زیر عضو شده اید:\n'
        for i in entities:
            TEXT +=  tasks.get_link(user,i) + '\n'
    else:
        TEXT = '''
        شما در دسته ای عضو نشده اید.
        '''
    send_telegram(bot, msg, TEXT, None)


def change_entity(bot, msg, entity , type = 'fallow' ):
    buttons = [[
        InlineKeyboardButton(text='۱', callback_data='score-'+str(entity.id)+'-(-2)'),
        InlineKeyboardButton(text='۲', callback_data='score-'+str(entity.id)+'-(-1)'),
        InlineKeyboardButton(text='۳', callback_data='score-'+str(entity.id)+'-(0)'),
        InlineKeyboardButton(text='۴', callback_data='score-'+str(entity.id)+'-(1)'),
        InlineKeyboardButton(text='۵', callback_data='score-'+str(entity.id)+'-(2)'),
         ],]
    keyboard = InlineKeyboardMarkup(buttons)
    if type == 'fallow':
        TEXT = '''
دسته %s نظر اضافه شد.
برای حذف کردن بر روی لینک %s کلیک کنید.
        ''' % (entity.name, "/remove_"+str(entity.id))
        return send_telegram(bot, msg, TEXT, keyboard)
    else:
        TEXT = '''
        دسته %s حذف شد.
        برای اضافه کردن مجدد بر روی لینک %s کلیک کنید.
        ''' % (entity.name,"/add_"+str(entity.id))
        return send_telegram(bot, msg, TEXT, keyboard)




def error_text(bot, msg, type = None):
    TEXT = 'ERROR'
    if type == 'NoEntity':
        TEXT = '''
        دسته مورد نظر موجود نمی‌باشد.
        '''
    elif type == 'LongMessage':
        TEXT= '''
        نتیجه درخواست شما بسیار طولانی است.
        و امکان ارسال آن وجود ندارد.
        '''
    elif type =='NoCommand':
        TEXT='''
        <b>همچین دستوری تعریف نشده است.</b>
        '''
    elif type =='PriorFallow':
        TEXT = '''
        شما قبلا این دسته را اضافه کرده اید.
        '''
    elif type == 'NoFallow':
        TEXT = '''
        شما این دسته را دنبال نمی کرده اید.
        '''
    return send_telegram(bot, msg, TEXT, None)

def help(bot, msg,user):
    menu = [
        ('/list' , 'تمام دسته هایی که عضو شده اید.'),
        ('/help', 'صفحه‌ی راهنمایی'),
        ('/live' ,'مشاهده‌ی اخبار به صورت لحظه‌ای'),
    ]
    text = 'راهنمایش ربات'+'\n'
    for i in menu:
        text += i[0] + ' ' + '<i>' + i[1] +'</i>\n'
    send_telegram_user(bot, user, text, None)


def news_page(News, page=1):
    buttons = [[
        InlineKeyboardButton(text='پسند', callback_data='news-' + str(News.id) + '-like')],
        [
            InlineKeyboardButton(text='خلاصه', callback_data='news-' + str(News.id) + '-overview'),
            InlineKeyboardButton(text='متن کامل خبر', callback_data='news-' + str(News.id) + '-full'),
            InlineKeyboardButton(text='آمار', callback_data='news-' + str(News.id) + '-stat'),
    ], ]
    keyboard = InlineKeyboardMarkup(buttons)
    TEXT = News.base_news.title + '\n'
    if page == 1:
        TEXT += News.summary + '\n'
    elif page == 2:
        TEXT += News.body[0:1000] + '\n' + 'ادامه دارد'
    elif page == 3:
        TEXT += str(News.pic_number) + '\n'
    TEXT = TEXT + '@mybot بات من'
    return keyboard, TEXT

def publish_news(bot, News, User, page=1, message_id=None):
    keyboard, Text = news_page(News, page)
    send_telegram_user(bot, User, Text, keyboard, message_id)

def send_telegram(bot, msg, Text , keyboard=None):
    if len(Text) > 4096 :
        error_text(msg,type="LongMessage")
        return False
    return bot.sendMessage(chat_id=msg.message.chat_id,
                           text = Text,
                           reply_markup=keyboard,
                           parse_mode =telegram.ParseMode.HTML)

def send_telegram_user(bot, User, Text , keyboard=None, message_id=None):
    profile = UserProfile.objects.get(user=User)
    id = profile.telegram_id
    if id:
        if not message_id:
            return bot.sendMessage(chat_id=id,
                               text = Text,
                               reply_markup=keyboard,
                               parse_mode = telegram.ParseMode.HTML)
        else:
            bot.editMessageText(text=Text,
                                chat_id=id,
                                message_id=message_id,
                                reply_markup=keyboard,
                                parse_mode=telegram.ParseMode.HTML,
                                inline_message_id=None)


def send_telegram_alluser(bot, Text , keyboard=None, Photo=None):
    allprofile = UserProfile.objects.all()
    for profile in allprofile:
        id = profile.telegram_id
        if id:
            if Photo:
                bot.sendPhoto(chat_id=id,
                              photo=Photo,
                              caption=Text[0:199],
                              reply_markup=keyboard,
                              parse_mode=telegram.ParseMode.HTML)
            else:
                bot.sendMessage(chat_id=id,
                                   text = Text,
                                   reply_markup=keyboard,
                                   parse_mode = telegram.ParseMode.HTML)
