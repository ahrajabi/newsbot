from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto
from rss.models import BaseNews, ImageUrls
from rss.models import News
from rss import elastic
from django.conf import settings
from telegrambot import news_template, bot_template
from telegram import ParseMode

def handler(bot, msg):
    query = msg.inline_query.query
    if not query:
        return

    el_news = elastic.news_with_terms(terms_list=[query],
                                      size=5,
                                      start_time='now-3h')

    try:
        news_ent = [item['_id'] for item in el_news['hits']['hits']]
    except Exception:
        print("ES DIDNT RETURN RIGHT JSON! See publish.py")
        return False

    print("_________", query, len(news_ent))
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query,
            title="لیست جدیدترین خبر‌های %s"%(query),
            input_message_content=InputTextMessageContent(
                news_template.prepare_multiple_sample_news(news_ent, settings.NEWS_PER_PAGE, inline=True)[0],
                parse_mode=ParseMode.HTML
            )
        )
    )
    print(el_news)
    for item in el_news['hits']['hits']:
        news_themed = bot_template.inline_news_page(item['_id'])
        if not news_themed:
            continue
        results.append(
            InlineQueryResultArticle(
                id=item['_id'],
                title=item['_source']['title'],
                input_message_content=InputTextMessageContent(news_themed[0], parse_mode=ParseMode.HTML),
        #        reply_markup=news_themed[1]
            )
        )

    ret = bot.answerInlineQuery(msg.inline_query.id, results, switch_pm_text="خبرِمن")
