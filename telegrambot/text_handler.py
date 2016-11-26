from telegram.emoji import Emoji
from telegram import InlineKeyboardMarkup
from telegram.inlinekeyboardbutton import InlineKeyboardButton
import datetime
from django.db.models import Q
from entities.models import Entity
from rss.ml import normalize
from telegrambot.bot_template import prepare_advice_entity_link
from telegrambot.news_template import prepare_multiple_sample_news
from rss.elastic import elastic_search_entity, similar_news_to_query, entity_validation_search
from newsbot.settings import SAMPLE_NEWS_COUNT, MIN_HITS_ENTITY_VALIDATION, DAYS_FOR_SEARCH_NEWS
from telegrambot.bot_send import send_telegram_user, error_text
from newsbot.settings import MAIN_BUTTONS
from telegrambot import command_handler
from telegrambot.models import UserSearchList
from django.utils import timezone
from django.conf import settings
from entities.tasks import get_link
from rss.ml import word_tokenize


def handle(bot, update):
    if hasattr(update, 'ignore'):
        return
    user = update.message.chat.up.user
    # TODO set len hits
    text = update.message.text
    if text == MAIN_BUTTONS[0][0]:
        getattr(command_handler, MAIN_BUTTONS[0][1])(bot, update, user)
    elif text == MAIN_BUTTONS[1][0]:
        getattr(command_handler, MAIN_BUTTONS[1][1])(bot, update, user)
    elif text == MAIN_BUTTONS[2][0]:
        getattr(command_handler, MAIN_BUTTONS[2][1])(bot, update, user)
    elif text == MAIN_BUTTONS[3][0]:
        getattr(command_handler, MAIN_BUTTONS[3][1])(bot, update, user)
    elif text == MAIN_BUTTONS[4][0]:
        getattr(command_handler, MAIN_BUTTONS[4][1])(bot, update, user)
    else:
        search_box_result(bot, update, user)


def search_box_result2(bot, update, user, msg_id=None, text=None):

    if not text:
        text = normalize(update.message.text)
    en_validation_hits = entity_validation_search(text, MIN_HITS_ENTITY_VALIDATION+1)

    response = ""

    no_response = False
    elastic_query = '0'
    if len(en_validation_hits) >= MIN_HITS_ENTITY_VALIDATION:
        hits = elastic_search_entity(text, SAMPLE_NEWS_COUNT + 1)

        h_response, h_response_len = prepare_multiple_sample_news(list(map(int, [hit['_id'] for hit in hits])),
                                                                  SAMPLE_NEWS_COUNT)
        from django.db.models import Q
        entity = Entity.objects.filter(Q(name=text, status='A'))
        if entity:
            response += Emoji.BOOKMARK
            response += "با انتخاب دسته زیر ، اخبار مرتبط به صورت بر خط برای شما ارسال خواهد شد."
            response += '\n' + prepare_advice_entity_link(entity[0]) + '\n'
            response += (5 * Emoji.HEAVY_MINUS_SIGN)
        response += '\n' + h_response
    else:
        no_response = True

    if not en_validation_hits or no_response:
        elastic_query = '1'
        similar_news_id = similar_news_to_query(text, SAMPLE_NEWS_COUNT, DAYS_FOR_SEARCH_NEWS)
        if not similar_news_id:
            error_text(bot, update, user, 'InvalidEntity')
            return

    final_destination = None
    call_back_id = None
    if update.callback_query is not None:
        final_destination = update.callback_query.message.message_id
        call_back_id = msg_id
    elif update.message is not None:
        call_back_id = update.message.message_id

    buttons = [[
        InlineKeyboardButton(text='صفحه بعد', callback_data='continue-' + 'next-1-' + elastic_query +
                                                            '-' + str(call_back_id)),
    ], ]
    keyboard = InlineKeyboardMarkup(buttons)

    if len(en_validation_hits) == SAMPLE_NEWS_COUNT:
        keyboard = None

    send_telegram_user(bot, user, response, update, keyboard, final_destination)


def search_box_result(bot, update, user, msg_id=None, text=None):
    del msg_id
    if not text:
        text = normalize(update.message.text)

    # def similar_news_to_query(query, size=10, days=7, end_time='now', offset=0, sort='_score'):
    similar_news = similar_news_to_query(text, settings.NEWS_PER_PAGE,
                                         start_time=timezone.now() - datetime.timedelta(days=DAYS_FOR_SEARCH_NEWS))

    try:
        news_ent = [item['_id'] for item in similar_news['hits']['hits']]
    except:
        print("ES DIDN'T RETURN RIGHT JSON! See publish.py")
        return False

    unl = UserSearchList.objects.create(user=user,
                                        query=text,
                                        datetime_start=timezone.now() - datetime.timedelta(days=DAYS_FOR_SEARCH_NEWS),
                                        datetime_publish=timezone.now(),
                                        number_of_news=similar_news['hits']['total'],
                                        order='N',
                                        page=1)

    if len(news_ent) > 0:
        news_list = news_ent

        output = prepare_multiple_sample_news(news_list, settings.NEWS_PER_PAGE)[0]
        keyboard = None
        print("HELLO")
        if similar_news['hits']['total'] > settings.NEWS_PER_PAGE:
            buttons = [
                [InlineKeyboardButton(text='به ترتیب زمان', callback_data='searchlist-time')],
                [InlineKeyboardButton(text='صفحه بعد', callback_data='searchlist-next')]
            ]
            keyboard = InlineKeyboardMarkup(buttons)

        result = send_telegram_user(bot, user, output, keyboard=keyboard)
        unl.message_id = result.message_id
        unl.save()
    else:
        output = Emoji.OK_HAND_SIGN + 'نتیجه‌ای در یک هفته‌ی اخیر یافت نشد.'
        send_telegram_user(bot, user, output)
    print("HMLLL")
    print(text)

    ent = Entity.objects.filter(Q(name__exact=text, status='A') | Q(synonym__name__exact=text, status='A'))
    for item in word_tokenize(text):
        ent = ent | Entity.objects.filter(Q(name__exact=item, status='A') | Q(synonym__name__exact=item, status='A'))

    text = 'نشان‌های مرتبط با جست و جوی شما' + '\n'
    if ent:
        print("RECOMMENDATION", ent)
        for item in ent.distinct():
            text += get_link(user, item) + '\n'

        rel = []
        for item in ent:
            if item.related:
                rel += item.related.all()
        print(rel)
        rel = list(set(rel))
        if rel:
            text += '\n' + 'نشان‌های نزدیک به جست و جوی شما' + '\n'
            for item in rel:
                text += get_link(user, item) + '\n'

        send_telegram_user(bot, user, text)
    else:
        print("NO RECOMM")
