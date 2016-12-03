import telegram
from telegram.emoji import Emoji
from telegram import ReplyKeyboardMarkup

from telegrambot.models import UserProfile, UserNews
from newsbot.settings import MAIN_BUTTONS
from telegrambot import bot_info


def default_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [
            MAIN_BUTTONS[4][0],
            # MAIN_BUTTONS[0][0]
        ]
    ], resize_keyboard=True)


def send_telegram_user(bot, user, text, update=None, keyboard=None, message_id=None, photo=None, ps=True):
    if user and keyboard is None:
        keyboard = default_keyboard()
    if ps:
        text += '\n\n' + bot_info.botpromote
    if len(text) > 4096:
        error_text(bot, update, user, error_type="LongMessage")
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

                # bot.editMessageReplyMarkup(chat_id=p_id,
                #                            message_id=message_id,
                #                            reply_markup=keyboard)
        else:
            bot.sendPhoto(chat_id=p_id,
                          photo=photo,
                          caption=text[0:199],
                          reply_markup=keyboard,
                          parse_mode=telegram.ParseMode.HTML)


def error_text(bot, update, user, error_type=None):
    text = 'ERROR'
    if error_type == 'NoEntity':
        text = '''       متن مورد نظر صحیح نمی‌باشد.'''

    elif error_type == 'LongMessage':
        text = '''
        نتیجه درخواست شما بسیار طولانی است.
        و امکان ارسال آن وجود ندارد.
        '''

    elif error_type == 'NoCommand':
        text = '''
         چنین دستوری تعریف نشده است %s
⁉️ راهنمایی را ببینید
        ''' % Emoji.WARNING_SIGN

    elif error_type == 'PriorFollow':
        text = '''
        شما قبلا این دسته را اضافه کرده اید!
        '''
    elif error_type == 'NoFallow':
        text = '''
        شما این دسته را دنبال نمی کرده اید.
        '''
    elif error_type == 'InvalidEntity':
        text = ''' دسته وارد شده مورد قبول نیست %s ''' % Emoji.NO_ENTRY_SIGN

    elif error_type == 'RepetitiveStart':
        text = '''شما قبلا وارد شده ایدبرای استفاده بهتر
⁉️ راهنمایی را ببینید
'''

    elif error_type == 'NoneNews':
        text = "خبر مورد نظر موجود نمی باشد!"

    elif error_type == 'NoNews':
        text = '''
خبری برای شما موجود نمی‌باشد.
        '''
    elif error_type == 'NoCategory':
        text = '''
شما هیچ دسته‌بندی انتخاب نکرده اید. برای این کار /categories را لمس نمایید.
            '''
    elif error_type == 'NoneEntity':
        text = ''' شما هیچ نشانی را دنبال نمیکنید %s و فعال سازی اخبار زنده امکان پذیر نمی‌باشد.
        می توانید موضوعات مورد علاقه خود (مثل پتروشیمی، محسن چاوشی، دیابت، تراکتورسازی تبریز و ...) را تایپ کنید %s و با افزودن آن‌ها به لیست، دنبال نمایید.
        ''' % (Emoji.FACE_SCREAMING_IN_FEAR, Emoji.WHITE_DOWN_POINTING_BACKHAND_INDEX)
    return send_telegram_user(bot, user, text, update, keyboard=None)


def send_telegram_chat(bot, chat_id, text, keyboard=None, message_id=None, photo=None, ps=True):
    if not keyboard:
        keyboard = default_keyboard()

    if keyboard == -1:
        keyboard = None
    if ps:
        text += '\n\n' + bot_info.botpromote
    if len(text) > 4096:
        return False
    if chat_id:
        if photo is None:
            if not message_id:
                return bot.sendMessage(chat_id=chat_id,
                                       text=text,
                                       reply_markup=keyboard,
                                       parse_mode=telegram.ParseMode.HTML)
            else:
                bot.editMessageText(text=text,
                                    chat_id=chat_id,
                                    message_id=message_id,
                                    reply_markup=keyboard,
                                    parse_mode=telegram.ParseMode.HTML)
        else:
            bot.sendPhoto(chat_id=chat_id,
                          photo=photo,
                          caption=text[0:199],
                          reply_markup=keyboard,
                          parse_mode=telegram.ParseMode.HTML)
