

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup
from entities import tasks
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
    text = 'راهنمای ربات'+'\n'
    for i in menu:
        text += i[0] + ' ' + '<i>' + i[1] +'</i>\n'
    send_telegram(bot, msg,text,None)

def send_telegram(bot, msg, Text , keyboard=None):
    if len(Text) > 4096 :
        error_text(msg,type="LongMessage")
        return False
    return bot.sendMessage(chat_id=msg.message.chat_id,
                           text = Text,
                           reply_markup=keyboard,
                           parse_mode = telegram.ParseMode.HTML)

def send_telegram_user(bot, user, Text , keyboard=None):

    return bot.sendMessage(chat_id=user.userprofile_set ,
                           text = Text,
                           reply_markup=keyboard,
                           parse_mode = telegram.ParseMode.HTML)