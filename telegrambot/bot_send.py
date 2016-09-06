import telegram
from telegram.emoji import Emoji
from telegram import ReplyKeyboardMarkup

from telegrambot.models import UserProfile, UserNews


def send_telegram(bot, msg, text, keyboard=None):
    keyboard = ReplyKeyboardMarkup(keyboard=[[
    '/HELP ⁉️ راهنمایی',
     ]], resize_keyboard=True)

    if len(text) > 4096:
        error_text(msg, type="LongMessage")
        return False
    return bot.sendMessage(chat_id=msg.message.chat_id,
                           text=text,
                           reply_markup=keyboard,
                           parse_mode=telegram.ParseMode.HTML)


def send_telegram_user(bot, user, text, keyboard=None, message_id=None, photo=None):
    profile = UserProfile.objects.get(user=user)
    p_id = profile.telegram_id

    if p_id:
        if photo==None:
            if not message_id:
                return bot.sendMessage(chat_id=p_id,
                                       text=text,
                                       reply_markup=keyboard,
                                       parse_mode=telegram.ParseMode.HTML)
            else:
                bot.editMessageText(text=text,
                                    chat_id=p_id,
                                    message_id=message_id,
                                    reply_markup=keyboard,
                                    parse_mode=telegram.ParseMode.HTML,
                                    inline_message_id=None)
        else:
            bot.sendPhoto(chat_id=p_id,
                          photo=photo,
                          caption=text[0:199],
                          reply_markup=keyboard,
                          parse_mode=telegram.ParseMode.HTML)


def send_telegram_all_user(bot, text, keyboard=None, photo=None):
    all_profile = UserProfile.objects.all()
    for profile in all_profile:
        id = profile.telegram_id
        if id:
            if photo:
                bot.sendPhoto(chat_id=id,
                              photo=photo,
                              caption=text[0:199],
                              reply_markup=keyboard,
                              parse_mode=telegram.ParseMode.HTML)
            else:
                bot.sendMessage(chat_id=id,
                                text=text,
                                reply_markup=keyboard,
                                parse_mode=telegram.ParseMode.HTML)


def error_text(bot, msg, type=None):
    text = 'ERROR'
    if type == 'NoEntity':
        text = '''        دسته مورد نظر موجود نمی‌باشد.'''

    elif type == 'LongMessage':
        text = '''
        نتیجه درخواست شما بسیار طولانی است.
        و امکان ارسال آن وجود ندارد.
        '''

    elif type == 'NoCommand':
        text = '''
         چنین دستوری تعریف نشده است %s
⁉️ راهنمایی را ببینید
        ''' % Emoji.WARNING_SIGN

    elif type == 'PriorFollow':
        text = '''
        شما قبلا این دسته را اضافه کرده اید!
        '''
    elif type == 'NoFallow':
        text = '''
        شما این دسته را دنبال نمی کرده اید.
        '''
    elif type == 'InvalidEntity':
        text = ''' دسته وارد شده مورد قبول نیست %s ''' % Emoji.NO_ENTRY_SIGN

    elif type == 'RepetitiveStart':
        text = '''شما قبلا وارد شده ایدبرای استفاده بهتر
⁉️ راهنمایی را ببینید
'''

    elif type == 'NoneNews':
        text = "خبر مورد نظر موجود نمی باشد!"
    return send_telegram(bot, msg, text, None)

