from telegram.emoji import Emoji
import jdatetime
from rss.models import News
from telegrambot.bot_send import send_telegram
from telegrambot import bot_info
import locale
from django.utils import timezone
from rss.ml import normalize
from django.conf import settings

def GeorgianToJalali(datetime):
    jal = jdatetime.GregorianToJalali(datetime.year, datetime.month, datetime.day)
    locale.setlocale(locale.LC_ALL, "fa_IR")
    ret =  jdatetime.datetime(jal.jyear, jal.jmonth, jal.jday).strftime("%a, %d %b") + ' ' + \
           timezone.localtime(datetime).strftime("%M:%-H")
    return normalize(ret)



def sample_news_page(news, inline=False):
    title = news.base_news.title

    try:
        source = news.base_news.news_agency.fa_name
    except Exception:
        try:
            source = news.base_news.rss.news_agency.fa_name
        except Exception:
            pass

    text = ''
    if not inline:
        text = Emoji.SMALL_BLUE_DIAMOND + title + '\n'
    text += '    ' + news.get_summary() + '\n'
    text += '    ' + Emoji.CALENDAR + ' ' + GeorgianToJalali(news.base_news.published_date) + '\n'
    try:
        text += '    ' + Emoji.WHITE_HEAVY_CHECK_MARK + 'منبع:‌ ' + source + '\n'
    except Exception:
        pass
    if not inline:
        text += '    ' + Emoji.PUBLIC_ADDRESS_LOUDSPEAKER + 'مشاهده خبر:' + '/News_' + str(news.id) + '\n'
    else:
        #https://telegram.me/chvotebot?start=f9830f23b29d139df0377496211a599b9eddeb5e2eb75ce71e12
        text += '    ' + Emoji.PUBLIC_ADDRESS_LOUDSPEAKER +\
                '<a href=' +'"https://telegram.me/'+settings.BOT_NAME[1:]+'?start=' +'N' + str(news.id) +'">' + 'مشاهده‌ی سریع خبر' + '</a>\n'

    return text +'\n'


def prepare_multiple_sample_news(news_id_list, total_news, inline=False):
    "just prepare multiple news"
    news_count = 0
    text = ''
    for news_id in news_id_list:
        try:
            text += sample_news_page(News.objects.get(id=news_id), inline)
            news_count += 1
            if news_count >= total_news:
                break
        except News.DoesNotExist:
            continue

    text += '\n'
    text += bot_info.botpromote
    return text, news_count


def publish_sample_news(bot, msg, news_id_list, total_news, keyboard=None):
    text = "%s خبرهای مرتبط:\n" % Emoji.NEWSPAPER
    text += prepare_multiple_sample_news(news_id_list, total_news)
    send_telegram(bot, msg, text, keyboard=None)
