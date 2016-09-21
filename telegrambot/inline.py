from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto
from rss.models import BaseNews, ImageUrls
from rss.models import News
def handler(bot, msg):
    query = msg.inline_query.query
    if not query:
        return

    newses = News.objects.filter(base_news__title__contains=query)
    print("_________", query, newses.count())
    results = list()
    for item in newses[0:40]:
        if item.pic_number == 0:
            results.append(
                InlineQueryResultArticle(
                    id=item.id,
                    title=item.base_news.title,
                    input_message_content=InputTextMessageContent(item.body[0:250])
                )
            )
        else:

            photo = ImageUrls.objects.filter(news=item)[0]

            if not photo.img_url.startswith('http'):
                continue
            results.append(
                InlineQueryResultPhoto(
                    id=item.id,
                    photo_url=photo.img_url,
                    thumb_url=photo.img_url,
                    caption=item.body[0:200],

                )
            )
    bot.answerInlineQuery(msg.inline_query.id, results, switch_pm_text="heyyy")
