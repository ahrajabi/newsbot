from django.conf import settings
from telegram import ReplyKeyboardMarkup, KeyboardButton

from rss.ml import normalize
from telegrambot import bot_send
from entities.tasks import set_entity
from entities.models import Entity, UserEntity
from telegrambot.models import UserProfile, MessageFromUser
from telegrambot.publish import prepare_periodic_publish_news
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

X1, X2, E = range(3)


def keyboard_symbols():
    symbols_list = ['آسیا', 'آپ', 'بفجر', 'ثاژن', 'حتوکا', 'خبهمن', 'خریخت', 'خزامیا', 'خودرو', 'خودرو2', 'خوساز',
                    'خپارس', 'خگستر', 'دانا', 'شبندر', 'شتران', 'شپنا', 'غالبر', 'غشاذر', 'فاذر', 'فاراک', 'فاسمین',
                    'فخوز', 'فلوله', 'فملی', 'فملی2', 'فولاد', 'فولاد2', 'فولاژ', 'قزوین', 'همراه', 'واتی', 'وبانک',
                    'وبانک2', 'ورنا', 'وساپا', 'کاما', 'کسرا', 'کطبس', 'کچاد', 'کگل']
    # Todo show entities base on followers of them
    key = Entity.objects.filter(synonym__name__in=symbols_list).order_by('synonym__name').values('synonym__name')
    buttons = [KeyboardButton(text=item['synonym__name']) for item in key]
    but = list()
    for nu, item in enumerate(buttons[::2]):
        but.append(buttons[2 * nu:2 * nu + 2])
    return ReplyKeyboardMarkup(but)


def choose_symbols(bot, update):
    up = UserProfile.objects.get(telegram_id=update.message.chat.id)
    user = up.user

    MessageFromUser.objects.create(user=user,
                                   message_id=update.message.message_id,
                                   chat_id=update.message.chat_id,
                                   type=2,
                                   message=update.message.text)

    text = ''
    if update.message.text == '/symbols':
        text += '''
        برای شروع نیاز هست که حداقل سه نماد بورسی را به لیست نشان‌های خود اضافه نمایید.
        برای این کار می‌توانید نام آن را تایپ کنید یا از منو انتخاب نمایید.
        '''
        bot_send.send_telegram_user(bot, user, text, keyboard=keyboard_symbols(), ps=False)
        return X1

    ue = UserEntity.objects.filter(user=user, status=True)
    if ue.count() >= settings.REQUIRED_ENTITY:
        print("FINISHED")
        return ConversationHandler.END

    try:
        ee = Entity.objects.get(synonym__name__in=[normalize(update.message.text)])
        set_entity(user, ee.id, mark=True)
        text += 'نماد ' + ee.synonym.all()[0].name + ' برای شما ثبت شد.'
        text += '\n'
        if ue.count() >= settings.REQUIRED_ENTITY:
            text += '''
هر سه نماد به درستی به نشان‌های شما اضافه شدند.
از این پس اخبار جدید مرتبط با نشان‌های شما به صورت زنده ارسال می‌شود.

امکانات روبات به شرح زیر برای شما فعال شده است:
✳️ جست و جوی اخبار - کافیست متن مورد نظر خود را تایپ نمایید تا اخبار مرتبط را دریافت کنید.

✳️ مدیریت نشان‌ها - با دستور /list می‌توانید نشان‌های خود را مشاهده و مدیریت نمایید. برای اضافه کردن نشان جدید کافیست نام آن را تایپ نمایید.

✳ افزونه گوگل - از طریق افزونه گوگل می‌توانید اخبار را هرچه سریع‌تر دریافت نمایید.

✳ کانال‌های تلگرام - علاوه بر سایت‌های خبری، منابع روبات تلگرام شامل کانال‌های معتبر تلگرام نیز می‌باشد.

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
    bot_send.send_telegram_user(bot, user, normalize(text), keyboard=keyboard_symbols(), ps=False)
    return X1


SYMBOL_WIZARD = ConversationHandler(
    entry_points=[CommandHandler('symbols', choose_symbols)],
    states={
        X1: [MessageHandler(Filters.text, choose_symbols),
             CommandHandler('next', choose_symbols)],
    },
    fallbacks=[CommandHandler('exit', choose_symbols)]
)
