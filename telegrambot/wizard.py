from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
from telegrambot import bot_send
from rss.models import CategoryCode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegrambot.models import UserProfile
from telegram.emoji import Emoji
from django.core.cache import cache
from entities.models import Entity, UserEntity
from rss.ml import normalize
from entities.tasks import set_entity
from django.conf import settings
from telegrambot.models import MessageFromUser
X1, X2, E = range(3)


def category_page(bot, msg, user, level=1):
    comm = '/next'
    # if level==1:
    #     comm = '/next'
    # else:
    #     comm = '/exit'

    text = 'دسته‌بندی‌های خبری مورد علاقه‌ی خود را فعال'
    text += ' و '
    text += 'در انتها %s را لمس نمایید.' % comm

    up = UserProfile.objects.get(user=user)
    cc = CategoryCode.objects.filter(level=level, activation=True).order_by('id')
    xx = []
    for item in cc:
        if item.parent and not item.parent.name == 'all':
            if not item.parent in up.interest_categories.all():
                continue

        if item in up.interest_categories.all():
            tt = Emoji.FULL_MOON_SYMBOL
        else:
            tt = Emoji.NEW_MOON_SYMBOL

        xx.append(InlineKeyboardButton(text=tt + ' ' + item.fa_name,
                                       callback_data='category-' + str(item.id) + '-' + str(level)))
    if len(xx) == 0:
        return None, None
    buttons = []
    for nu, item in enumerate(xx[::2]):
        buttons.append(xx[2 * nu:2 * nu + 2])
    keyboard = InlineKeyboardMarkup(buttons)

    return text, keyboard


def choose_category(bot, msg):
    user = UserProfile.objects.get(telegram_id=msg.message.chat.id).user
    up = UserProfile.objects.get(user=user)

    try:
        cache.incr('w' + str(up.telegram_id))
    except Exception:
        cache.set('w' + str(up.telegram_id), 1)
    level = cache.get('w' + str(up.telegram_id))

    text, keyboard = category_page(bot, msg, user, level=level)
    if keyboard:
        bot_send.send_telegram_user(bot, user, text, keyboard=keyboard, ps=False)
        return X1
    else:
        categories_list(bot, msg)
        return ConversationHandler.END


def categories_list(bot, msg):
    up = UserProfile.objects.get(telegram_id=msg.message.chat.id)
    user = up.user
    cache.delete('w' + str(up.telegram_id))
    if up.interest_categories.all().count() == 0:
        bot_send.send_telegram_user(bot, user, 'هیچ دسته بندی برای شما ثبت نشده است.')
        return ConversationHandler.END
    text = 'دسته‌بندی های انتخابی شما به شرح زیر ثبت شد: \n'
    node = CategoryCode.objects.get(name='all')
    for item in node.get_children():
        if item in up.interest_categories.all():
            text += '-  ' + item.fa_name + '\n'
            for item2 in item.get_children():
                if item2 in up.interest_categories.all():
                    text += '-  -  ' + item2.fa_name + '\n'
            text += '\n'

    text += 'از این پس می‌توانید از طریق دکمه‌ی 🌟 خبر ویژه در منوی اصلی اخبار را بخوانید.'
    bot_send.send_telegram_user(bot, user, text)

    return ConversationHandler.END


CONV_WIZARD = ConversationHandler(
    entry_points=[CommandHandler('categories', choose_category)],
    states={
        X1: [MessageHandler([Filters.text], choose_category),
             CommandHandler('next', choose_category)],
    },
    fallbacks=[CommandHandler('exit', categories_list)]
)


def keyboard_namad():
    symlist = ['آسیا', 'آپ', 'بفجر', 'ثاژن', 'حتوکا', 'خبهمن', 'خریخت', 'خزامیا', 'خودرو', 'خودرو2', 'خوساز', 'خپارس',
               'خگستر', 'دانا', 'شبندر', 'شتران', 'شپنا', 'غالبر', 'غشاذر', 'فاذر', 'فاراک', 'فاسمین', 'فخوز', 'فلوله',
               'فملی', 'فملی2', 'فولاد', 'فولاد2', 'فولاژ', 'قزوین', 'همراه', 'واتی', 'وبانک', 'وبانک2', 'ورنا',
               'وساپا', 'کاما', 'کسرا', 'کطبس', 'کچاد', 'کگل']

    key = Entity.objects.filter(synonym__name__in=symlist).order_by('synonym__name').values('synonym__name')
    buttons = [KeyboardButton(text=item['synonym__name']) for item in key]
    but = list()
    for nu, item in enumerate(buttons[::2]):
        but.append(buttons[2 * nu:2 * nu + 2])
    return ReplyKeyboardMarkup(but)


def choose_namad(bot, msg):
    comm = '/next'
    # if level==1:
    #     comm = '/next'
    # else:
    #     comm = '/exit'
    up = UserProfile.objects.get(telegram_id=msg.message.chat.id)
    user = up.user

    MessageFromUser.objects.create(user=user,
                                   message_id=msg.message.message_id,
                                   chat_id=msg.message.chat_id,
                                   type=2,
                                   message=msg.message.text)

    text = ''
    if msg.message.text == '/symbols':
        text += '''
        برای شروع نیاز هست که حداقل سه نماد بورسی را به لیست نشان‌های خود اضافه نمایید.
        برای این کار می‌توانید نام آن را تایپ کنید یا از منو انتخاب نمایید.
        '''
        bot_send.send_telegram_user(bot, user, text, keyboard=keyboard_namad(), ps=False)
        return X1

    ue = UserEntity.objects.filter(user=user, status=True)
    if ue.count() >= settings.REQUIRED_ENTITY:
        # categories_list(bot, msg)
        print("FINISHED")
        return ConversationHandler.END

    try:
        ee = Entity.objects.get(synonym__name__in=[normalize(msg.message.text)])
        set_entity(user, ee.id, mark=True)
        text += 'نماد #' + ee.synonym.all()[0].name + ' برای شما ثبت شد.'
        text += '\n'
        if ue.count() >= settings.REQUIRED_ENTITY:
            text += '''
هر سه نماد به درستی به نشان‌های شما اضافه شدند.

امکانات روبات به شرح زیر برای شما فعال شده است:
✳️ جست و جوی اخبار - کافیست متن مورد نظر خود را تایپ نمایید تا اخبار مرتبط را دریافت کنید.

✳️ مدیریت نشان‌ها - با دستور /list می‌توانید نشان‌های خود را مشاهده و مدیریت نمایید. برای اضافه کردن نشان جدید کافیست نام آن را تایپ نمایید.

✳️ دریافت اخبار - اخبار مرتبط با نشان‌های شما به صورت اتوماتیک ارسال می‌شود اما برای مشاهده‌ی دستی کافیست خبرهای نشان‌شده را لمس نمایید.

✳ افزونه گوگل - از طریق افزونه گوگل می‌توانید اخبار را هرچه سریع‌تر دریافت نمایید.

✳ کانال‌های تلگرام - به زودی کانال‌های معتبر تلگرام به منابع روبات تلگرام اضافه خواهد شد.

✳️ برای استفاده از امکانات بیشتر روبات، راهنما را لمس نمایید.
            '''
            bot_send.send_telegram_user(bot, user, text)
            return ConversationHandler.END
        else:
            text += '''
%s نماد ثبت شده است. %s نماد دیگر نیاز است که وارد نمایید.
برای این کار می‌توانید نام آن را تایپ کنید یا از منو انتخاب نمایید.
            ''' % (ue.count(), settings.REQUIRED_ENTITY - ue.count())
    except:
        text += 'برای مورد تایپ شده نمادی پیدا نشده است. لطفا مجددا با دقت وارد نمایید.'
    bot_send.send_telegram_user(bot, user, normalize(text), keyboard=keyboard_namad(), ps=False)
    return X1


SYMBOL_WIZARD = ConversationHandler(
    entry_points=[CommandHandler('symbols', choose_namad)],
    states={
        X1: [MessageHandler([Filters.text], choose_namad),
             CommandHandler('next', choose_namad)],
    },
    fallbacks=[CommandHandler('exit', choose_namad)]
)
