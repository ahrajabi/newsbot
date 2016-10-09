from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
from telegrambot import bot_send
from rss.models import CategoryCode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegrambot.models import UserProfile
from telegram.emoji import Emoji
from django.core.cache import cache

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
