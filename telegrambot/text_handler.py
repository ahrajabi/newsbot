from telegram.emoji import Emoji
from telegram import InlineKeyboardMarkup
from telegram.inlinekeyboardbutton import InlineKeyboardButton
import datetime

from entities.models import Entity
from rss.ml import normalize, word_tokenize, bi_gram, tri_gram
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


def handle(bot, msg, user):
    # TODO set len hits
    text = msg.message.text
    if text == MAIN_BUTTONS[0][0]:
        getattr(command_handler, MAIN_BUTTONS[0][1])(bot, msg, user)
    elif text == MAIN_BUTTONS[1][0]:
        getattr(command_handler, MAIN_BUTTONS[1][1])(bot, msg, user)
    elif text == MAIN_BUTTONS[2][0]:
        getattr(command_handler, MAIN_BUTTONS[2][1])(bot, msg, user)
    elif text == MAIN_BUTTONS[3][0]:
        getattr(command_handler, MAIN_BUTTONS[3][1])(bot, msg, user)
    elif text == MAIN_BUTTONS[4][0]:
        getattr(command_handler, MAIN_BUTTONS[4][1])(bot, msg, user)
    else:
        search_box_result(bot, msg, user)


def search_box_result2(bot, msg, user, msg_id=None, text=None):

    if not text:
        text = normalize(msg.message.text)
    en_validation_hits = entity_validation_search(text, MIN_HITS_ENTITY_VALIDATION+1)

    response = ""

    no_response = False
    elastic_query = '0'
    if len(en_validation_hits) >= MIN_HITS_ENTITY_VALIDATION:
        hits = elastic_search_entity(text, SAMPLE_NEWS_COUNT + 1)

        h_response, h_response_len = prepare_multiple_sample_news(list(map(int, [hit['_id'] for hit in hits])),
                                                                  SAMPLE_NEWS_COUNT)
        # entity = Entity.objects.get_or_create(name=text, wiki_name='')[0]
        from django.db.models import Q
        entity = Entity.objects.filter(Q(name=text, status ='A'))
        if entity:
            response += Emoji.BOOKMARK + \
                        "با انتخاب دسته زیر ، اخبار مرتبط به صورت بر خط برای شما ارسال خواهد شد." + \
                        '\n' + prepare_advice_entity_link(entity[0]) + '\n' + Emoji.HEAVY_MINUS_SIGN * 5 + '\n'
        response += '\n' + h_response
    else:
        no_response = True

    if not en_validation_hits or no_response:
        elastic_query = '1'
        similar_news_id = similar_news_to_query(text, SAMPLE_NEWS_COUNT, DAYS_FOR_SEARCH_NEWS)
        similar_news = prepare_multiple_sample_news(similar_news_id, 2)[0]

        def print_n_gram(n_gram):
            gram_response = ""
            not_response = True
            for word in n_gram:
                related_hits = entity_validation_search(word)
                if len(related_hits) >= MIN_HITS_ENTITY_VALIDATION:
                    en = Entity.objects.get_or_create(name=word, wiki_name='')[0]
                    gram_response += prepare_advice_entity_link(en) + '\n'
                    not_response = False

            return not_response, gram_response
        # pre_response = Emoji.WARNING_SIGN + "متن وارد شده یافت نشد.\n" + Emoji.BOOKMARK + \
        #                "دسته های مشابه پیشنهادی:‌\n با انتخاب هر یک اخبار مرتبط به صورت بر خط برای شما ارسال خواهد شد.\n"
        #
        # three_gram = tri_gram(text)
        # no_three_gram_response, three_response = print_n_gram(three_gram)
        # if no_three_gram_response:
        #     two_gram = bi_gram(text)
        #     no_two_gram_response, two_response = print_n_gram(two_gram)
        #     if no_two_gram_response:
        #         one_gram = word_tokenize(text)
        #         no_one_gram_response, one_response = print_n_gram(one_gram)
        #         if no_one_gram_response:
        #             if not similar_news_id:
        #                 error_text(bot, msg, user, 'InvalidEntity')
        #                 return
        #         else:
        #             response += pre_response + one_response
        #     else:
        #         response += pre_response + two_response
        # else:
        #     response += pre_response + three_response

        if not similar_news_id:
            error_text(bot, msg, user, 'InvalidEntity')
            return

    final_destination = None
    call_back_id = None
    if msg.callback_query is not None:
        final_destination = msg.callback_query.message.message_id
        call_back_id = msg_id
    elif msg.message is not None:
        call_back_id = msg.message.message_id

    buttons = [[
        InlineKeyboardButton(text='صفحه بعد', callback_data='continue-' + 'next-1-' + elastic_query +
                                                            '-' + str(call_back_id)),
    ], ]
    keyboard = InlineKeyboardMarkup(buttons)

    if len(en_validation_hits) == SAMPLE_NEWS_COUNT:
        keyboard = None

    send_telegram_user(bot, user, response, msg, keyboard, final_destination)


def search_box_result(bot, msg, user, msg_id=None, text=None):
    if not text:
        text = normalize(msg.message.text)

    # def similar_news_to_query(query, size=10, days=7, end_time='now', offset=0, sort='_score'):
    similar_news = similar_news_to_query(text, settings.NEWS_PER_PAGE,
                                         start_time=timezone.now() - datetime.timedelta(days=DAYS_FOR_SEARCH_NEWS))

    try:
        news_ent = [item['_id'] for item in similar_news['hits']['hits']]
    except Exception:
        print("ES DIDNT RETURN RIGHT JSON! See publish.py")
        return False

    unl = UserSearchList.objects.create(user=user,
                                        query=text,
                                        datetime_start=timezone.now() - datetime.timedelta(days=DAYS_FOR_SEARCH_NEWS),
                                        datetime_publish=timezone.now(),
                                        number_of_news=similar_news['hits']['total'],
                                        order='N',
                                        page=1)

    if len(news_ent) > 0:
        news_list = list(set([item for item in news_ent]))

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

    ent = Entity.objects.filter(name__exact=text, status='A') | \
          Entity.objects.filter(synonym__name__exact=text, status='A')
    for item in word_tokenize(text):
        ent = ent | Entity.objects.filter(name__exact=item, status='A') | \
              Entity.objects.filter(synonym__name__exact=item, status='A')

    text = 'نشان‌های مرتبط با جست و جوی شما' + '\n'
    if ent:
        print("RECOMMENDATION", ent)
        for item in ent.distinct():
            text += get_link(user, item) + '\n'

        rel = []
        for item in ent:
            if item.related:
                rel += item.related.all()
        rel = list(set(rel))
        if rel:
            text += '\n' + 'نشان‌های نزدیک به جست و جوی شما' + '\n'
            for item in rel:
                text += get_link(user, item) + '\n'

        send_telegram_user(bot, user, text)
    else:
        print("NO RECOMM")
