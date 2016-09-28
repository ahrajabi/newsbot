import telegram
from telegram.emoji import Emoji
from telegram import ReplyKeyboardMarkup

from telegrambot.models import UserProfile, UserNews


def send_telegram_user(bot, user, text, msg=None, keyboard=None, message_id=None, photo=None):
    if keyboard is None:
        if UserProfile.objects.get(user=user).user_settings.live_news:
            live_button = '/Live قطع دریافت اخبار زنده'
        else:
            live_button = '/Live دریافت اخبار زنده'
        keyboard = ReplyKeyboardMarkup(keyboard=[
        [live_button],
        ['/HELP ⁉️ راهنمایی']
        ], resize_keyboard=True)

    if len(text) > 4096:
        error_text(bot, msg, user, type="LongMessage")
        return False

    profile = UserProfile.objects.get(user=user)
    p_id = profile.telegram_id

    if p_id:
        if photo is None:
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
                return bot.sendPhoto(chat_id=id,
                                     photo=photo,
                                     caption=text[0:199],
                                     reply_markup=keyboard,
                                     parse_mode=telegram.ParseMode.HTML)
            else:
                return bot.sendMessage(chat_id=id,
                                       text=text,
                                       reply_markup=keyboard,
                                       parse_mode=telegram.ParseMode.HTML)


def error_text(bot, msg, user, type=None):
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
    return send_telegram_user(bot, user, text, msg, keyboard=None)


def send_telegram_document(bot, user, msg, doc):
    p_id = UserProfile.objects.get(user=user).telegram_id
    bot.sendDocument(
        chat_id=p_id,
        document=doc,
        parse_mode=telegram.ParseMode.HTML
     )
