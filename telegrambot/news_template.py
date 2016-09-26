import locale
import jdatetime
from telegram.emoji import Emoji
from django.utils import timezone
from django.conf import settings

from rss.models import News
from rss.models import ImageUrls
from rss.news import is_liked_news
from newsbot.settings import BOT_NAME
from entities.models import NewsEntity
from rss.elastic import more_like_this
from telegrambot.models import UserNews
from rss.ml import normalize, sent_tokenize
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegrambot.bot_send import send_telegram, send_telegram_user


def georgian_to_jalali(datetime):
    jal = jdatetime.GregorianToJalali(datetime.year, datetime.month, datetime.day)
    locale.setlocale(locale.LC_ALL, "fa_IR")
    ret = jdatetime.datetime(jal.jyear, jal.jmonth, jal.jday).strftime("%a, %d %b") + ' ' + \
          timezone.localtime(datetime).strftime("%M:%-H")
    return normalize(ret)


def sample_news_page(news):
    title = news.base_news.title

    try:
        source = news.base_news.rss.news_agency.fa_name
    except Exception:
        pass

    text = Emoji.SMALL_BLUE_DIAMOND + title + '\n'
    text += '    ' + Emoji.CALENDAR + ' ' + georgian_to_jalali(news.base_news.published_date) + '\n'
    try:
        text += '    ' + Emoji.WHITE_HEAVY_CHECK_MARK + 'منبع:‌ ' + source + '\n'
    except Exception:
        pass
    text += '    ' + Emoji.PUBLIC_ADDRESS_LOUDSPEAKER + 'مشاهده خبر:' + '/News_' + str(news.id) + '\n'
    return text +'\n'


def prepare_multiple_sample_news(news_id_list, total_news):
    "just prepare multiple news"
    news_count = 0
    text = ''
    for news_id in news_id_list:
        try:
            text += sample_news_page(News.objects.get(id=news_id))
            news_count += 1
            if news_count >= total_news:
                break
        except News.DoesNotExist:
            continue
    text += '\n'
    return text, news_count


def publish_sample_news(bot, msg, news_id_list, total_news, keyboard=None):
    text = "%s خبرهای مرتبط:\n" % Emoji.NEWSPAPER
    text += prepare_multiple_sample_news(news_id_list, total_news)
    send_telegram(bot, msg, text, keyboard=None)


def news_image_page(bot, news, user, page=1, message_id=None):
    image_url = ImageUrls.objects.filter(news=news)
    if image_url:
        image_url = image_url[0].img_url
    else:
        image_url = settings.TELEGRAM_LOGO

    UserNews.objects.update_or_create(user=user, news=news, defaults={'image_page': page})

    text = "<a href= '%s'>''</a>" % image_url
    return text


def news_page(bot, news, user, page=1, message_id=None, **kwargs):
    like = InlineKeyboardButton(text=Emoji.THUMBS_UP_SIGN + "(" + normalize(str(news.like_count)) + ")",
                                callback_data='news-' + str(news.id) + '-like')

    if is_liked_news(news=news, user=user):
        like = InlineKeyboardButton(text=Emoji.THUMBS_DOWN_SIGN + "(" + normalize(str(news.like_count)) + ")",
                                    callback_data='news-' + str(news.id) + '-unlike')

    buttons = [
        [
            InlineKeyboardButton(text='خلاصه', callback_data='news-' + str(news.id) + '-overview'),
            InlineKeyboardButton(text='متن کامل خبر', callback_data='news-' + str(news.id) + '-full'),
         ],
        [
            InlineKeyboardButton(text='اخبار مرتبط', callback_data='news-' + str(news.id) + '-stat'),
            like,
            InlineKeyboardButton(text='لینک خبر', url=str(news.base_news.url)),
        ], ]

    keyboard = InlineKeyboardMarkup(buttons)
    text = ''
    if page == 1:
        summary = news.summary
        has_summary = True

        if not summary:
            summary = news.body[:500]
            has_summary = False

        text += Emoji.PUBLIC_ADDRESS_LOUDSPEAKER + news.base_news.title + '\n\n'

        for sentence in sent_tokenize(summary):
            text += Emoji.SMALL_BLUE_DIAMOND + sentence + '\n'
            if len(text) > 300 and not has_summary:
                break
        try:
            text += '\n' + Emoji.WHITE_HEAVY_CHECK_MARK + 'منبع:‌ ' + news.base_news.rss.news_agency.fa_name + '\n'
        except Exception:
            pass

        if 'user_entity' in kwargs:
            news_user_entity = NewsEntity.objects.filter(news=news, entity__in=kwargs['user_entity'])
            if news_user_entity:
                text += '\n' + Emoji.BOOKMARK + ' دسته های مشترک با علاقه مندی شما:\n'
                for en in news_user_entity:
                    text += en.entity.name + ', '
                text += '\n'
        try:
            text += news_image_page(bot, news, user, page=1, message_id=message_id)
        except Exception:
            print(Exception)

    elif page == 2:
        try:
            text += Emoji.PUBLIC_ADDRESS_LOUDSPEAKER + news.base_news.title + '\n\n    '
        except Exception:
            pass

        if len(news.body) < 3500:
            text += news.body + '\n'
        else:
            text += news.body[:3500].rsplit(' ', 1)[0]
            text += '\n' + 'ادامه دارد...' + '\n'
    elif page == 3:
        related = more_like_this(news.base_news.title, 5)
        text, notext = prepare_multiple_sample_news(related, 5)
    text += BOT_NAME

    send_telegram_user(bot, user, text, keyboard, message_id)
    UserNews.objects.update_or_create(user=user, news=news, defaults={'page': page})
