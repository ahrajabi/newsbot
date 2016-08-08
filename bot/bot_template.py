
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

def welcome_text():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Press me', callback_data='press')],
        [InlineKeyboardButton(text='Presh me', callback_data='presh')],
    ])

    WELCOME_TEXT = '''
    برای شروع لطفا بر روی موضوع های مورد علاقه‌یتان کلیک کنید. در آینده به راحتی می توانید موضوعات را اضافه ویا حذف نمایید.
    %s
    %s
    '''
    return keyboard, WELCOME_TEXT



