from telegram.emoji import Emoji
import jdatetime
from rss.models import News
from telegrambot.bot_send import send_telegram
import locale
from django.utils import timezone
from rss.ml import normalize

def GeorgianToJalali(datetime):
    jal = jdatetime.GregorianToJalali(datetime.year, datetime.month, datetime.day)
    locale.setlocale(locale.LC_ALL, "fa_IR")
    ret =  jdatetime.datetime(jal.jyear, jal.jmonth, jal.jday).strftime("%a, %d %b") + ' ' + \
           timezone.localtime(datetime).strftime("%M:%-H")
    return normalize(ret)



def sample_news_page(news):
    title = news.base_news.title

    try:
        source = news.base_news.rss.news_agency.fa_name
    except Exception:
        pass

    text = Emoji.SMALL_BLUE_DIAMOND + title + '\n'
    text += '    ' + Emoji.CALENDAR + ' ' + GeorgianToJalali(news.base_news.published_date) + '\n'
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
