from telegram.emoji import Emoji
from django.core.management.base import BaseCommand

from telegrambot.models import UserAlert
from newsbot.settings import BOT_NAME


class Command(BaseCommand):
    help = "add userAlert for new update bot"

    def handle(self, *args, **options):
        text = '''
            %s سلام
            %s تغییرات جدید بات خبری %s
            %s افزودن دکمه اخبار زنده که با فعال کردن آن اخبار مرتبط با دسته های شما در لحظه ارسال میشود.
            %s افزودن دکمه اخبار ویژه که با زدن دکمه آن خبرهای جدید و پربازدید برای شما ارسال میشود.
            %s افزودن دکمه لیست خبرها که ‌با زدن آن لیستی از خلاصه خبرهای مرتبط با دسته های شما ارسال میشود
            %s افزودن قابلیت دریافت چندین عکس در یک خبر
            %s افزودن منابع خبری بیشتر

        %s منتظر نظرات شما هستیم /contact
                                ''' % (
            Emoji.RAISED_HAND,
            Emoji.PUSHPIN,
            BOT_NAME,
            Emoji.DIGIT_ONE_PLUS_COMBINING_ENCLOSING_KEYCAP,
            Emoji.DIGIT_TWO_PLUS_COMBINING_ENCLOSING_KEYCAP,
            Emoji.DIGIT_THREE_PLUS_COMBINING_ENCLOSING_KEYCAP,
            Emoji.DIGIT_FOUR_PLUS_COMBINING_ENCLOSING_KEYCAP,
            Emoji.DIGIT_FIVE_PLUS_COMBINING_ENCLOSING_KEYCAP,
            Emoji.WINKING_FACE
        )
        UserAlert.objects.create(text=text)