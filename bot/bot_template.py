
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

def welcome_text():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Press me', callback_data='press'),
        InlineKeyboardButton(text='Presh me', callback_data='presh')],
    ])

    WELCOME_TEXT = '''
    برای شروع لطفا بر روی موضوع های مورد علاقه‌یتان کلیک کنید. در آینده به راحتی می توانید موضوعات را اضافه ویا حذف نمایید.
    %s
    %s
    '''
    return keyboard, WELCOME_TEXT



def show_entities(entities):
    keyboard = None
    links = list()
    for entity in entities:
        links.append(entity.name + " /add_" + str(entity._get_pk_val()) )
    text = '\n'.join(links)
    return keyboard, text




def error_text(type = None):
    if type == 'NoEntity':
        keyboard = None
        TEXT = '''
        دسته مورد نظر موجود نمی‌باشد.
        '''
        return keyboard, TEXT
    else:
        keyboard = None
        TEXT = "ERROR"
        return keyboard, TEXT
