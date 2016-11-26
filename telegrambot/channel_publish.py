from telegrambot.models import ChannelPublish
from rss.models import News
from telegrambot.news_template import news_page


def channel_publish_handler(bot, job):
    for item in ChannelPublish.objects.all():
        ne = News.objects.filter(id__gt=item.last_news)
        # print('channel', item.channel_username, item.last_news)
        maxi = item.last_news
        for news in ne:
            # print('news', news.id)
            # text, keyboard = news_page(bot, news, channel_username=item.channel_username)
            # send_telegram_user(bot, text, keyboard=keyboard)
            maxi = max(maxi, news.id)
        if maxi > item.last_news:
            item.last_news = maxi
            item.save()
