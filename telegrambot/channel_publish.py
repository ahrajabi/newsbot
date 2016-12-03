from telegrambot.models import ChannelPublish
from rss.models import News
from telegrambot.news_template import news_page, news_keyboard_channel
from telegrambot.bot_send import send_telegram_chat


def channel_publish_handler(bot, job):
    del job
    for item in ChannelPublish.objects.all():
        ne = News.objects.filter(id__gt=item.last_news)
        print('channel', item.channel_username, item.last_news)
        maxi = item.last_news
        for news in ne:
            if (news.base_news.source_type == 1 and not item.send_news_agency) or\
                    (news.base_news.source_type == 2 and not item.send_codal) or \
                    (news.base_news.source_type == 3 and not item.send_channel):
                continue
            text = news_page(news)
            keyboard = news_keyboard_channel(news)
            maxi = max(maxi, news.id)

            text += '\n✌'+'@'+item.channel_username
            send_telegram_chat(bot, '@'+item.channel_username, text, keyboard=keyboard, ps=False)

        if maxi > item.last_news:
            item.last_news = maxi
            item.save()
