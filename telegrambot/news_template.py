from telegram.emoji import Emoji

from rss.models import News
from telegrambot.bot_send import send_telegram


def sample_news_page(news):
    title = news.base_news.title
    source = news.base_news.rss.fa_name
    text = Emoji.SMALL_BLUE_DIAMOND + title + '\n'
    text += '    ' + Emoji.PUBLIC_ADDRESS_LOUDSPEAKER + 'مشاهده خبر:' + '/News_' + str(news.id) + '\n'
    text += '    ' + Emoji.WHITE_HEAVY_CHECK_MARK + 'منبع:‌ ' + source + '\n\n'
    return text


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
    return text, news_count


def publish_sample_news(bot, msg, news_id_list, total_news):
    text = "%s خبرهای مرتبط:\n" % Emoji.NEWSPAPER
    text += prepare_multiple_sample_news(news_id_list, total_news)
    send_telegram(bot, msg, text)
