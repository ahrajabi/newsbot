from telegram.emoji import Emoji
from telegrambot.models import UserProfile, UserNews
from entities import tasks
from telegrambot.bot_send import send_telegram_user
from telegrambot.news_template import news_page, news_keyboard


def show_user_entity(bot, msg, user, entities):
    if entities:
        text = 'نشان‌هایی که دنبال می‌کنید:\n'
        for i in entities:
            text += tasks.get_link(user, i) + '\n'
    else:
        text = ''' شما هیچ نشانی را دنبال نمی‌کنید %s
        می‌توانید موضوعات مورد علاقه خود (مثل پتروشیمی) را تایپ %s و سپس با افزودن آن به لیست نشان‌ها، دنبال نمایید.
        ''' % (Emoji.FACE_SCREAMING_IN_FEAR, Emoji.WHITE_DOWN_POINTING_BACKHAND_INDEX)
    send_telegram_user(bot, user, text, msg)


def change_entity(bot, msg, entity, user, change_type=True):
    if change_type:
        text = '''
دسته %s اضافه شد.
برای حذف کردن بر روی لینک %s کلیک کنید.
        ''' % (entity.name, "/remove_"+str(entity.id))
        return send_telegram_user(bot, user, text, msg)
    else:
        text = '''
        دسته %s حذف شد.
        برای اضافه کردن مجدد بر روی لینک %s کلیک کنید.
        ''' % (entity.name, "/add_"+str(entity.id))
        return send_telegram_user(bot, user, text, msg)


def bot_help(bot, msg, user):
    print("bot_help")
    up = UserProfile.objects.get(user=user)

    menu = [
        ('/list', 'لیست نشان‌ها', 'با استفاده از این گزینه، می‌توانید نشان‌های خود را مشاهده و حذف نمایید.'),
        ('/interval', 'زمان دریافت اخبار زنده', 'از این طریق می‌توانید بازه‌‌ی زمانی دریافت اخبار زنده را تنظیم کنید.'),
        ('/browser', 'افزونه‌ی مرورگر',
         'این گزینه نحوه‌ی استفاده از افزونه‌ی مرورگر را توضیح می‌دهد.'
         'برای دریافت توکن و نام کاربری این گزینه را لمس نمایید.'),
        ('/contact', 'تماس با ما', 'راه‌های ارتباطی تیم خبرِمن')
    ]

    if up:
        if not up.stopped:
            menu.append(('/stop', 'توقف', 'توقف دریافت پیام از روبات'))
        else:
            menu.append(('/active', ' ',
                         'دریافت پیام از روبات را متوقف کرده‌اید. توسط این گزینه می‌توانید این محدودیت را بردارید.'))
    text = Emoji.LEFT_POINTING_MAGNIFYING_GLASS + 'راهنما' + '\n\n'
    for i in menu:
        text += Emoji.WHITE_RIGHT_POINTING_BACKHAND_INDEX + i[0] + ' ' + i[1] + '\n❔' + i[2] + '\n\n'
    send_telegram_user(bot, user, text, msg)


def publish_news(bot, news, user, page=1, message_id=None, **kwargs):
    text = news_page(news, page, picture_number=0, **kwargs)
    keyboard = news_keyboard(news, user, page, picture_number=0)
    UserNews.objects.update_or_create(user=user, news=news, defaults={'page': 1, 'image_page': 1})
    send_telegram_user(bot, user, text, keyboard=keyboard, message_id=message_id)


def after_user_add_entity(bot, msg, user, entity, entities):
    text = "دسته ' %s ' اضافه شد %s" % (entity, Emoji.PUSHPIN)
    send_telegram_user(bot, user, text, msg)
    show_user_entity(bot, msg, user, entities)


def prepare_advice_entity_link(entity):
    return Emoji.SMALL_ORANGE_DIAMOND + "/add_"+str(entity.id)+" " + entity.name + ""


def show_related_entities(related_entities):
    text = Emoji.HEAVY_MINUS_SIGN * 6 + Emoji.WHITE_LEFT_POINTING_BACKHAND_INDEX
    text += " دسته های مرتبط "
    text += Emoji.WHITE_RIGHT_POINTING_BACKHAND_INDEX + Emoji.HEAVY_MINUS_SIGN * 6
    text += '''
     %s نشان‌های مرتبط با متن وارد شده در زیر آمده است.
    با انتخاب هرکدام، می‌توانید اخبار مرتبط با آن را به صورت بر خط دنبال نمایید.\n''' % Emoji.BOOKMARK
    # for entity in (related_entities.sort(key=lambda e: e.followers, reverse=True)):
    for entity in related_entities:
        text += prepare_advice_entity_link(entity) + '\n'
    return text
