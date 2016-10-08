from telegram.emoji import Emoji
from telegram import InlineKeyboardMarkup
from telegram.inlinekeyboardbutton import InlineKeyboardButton

from entities.models import Entity
from rss.ml import normalize, word_tokenize, bi_gram, tri_gram
from telegrambot.bot_template import prepare_advice_entity_link
from telegrambot.news_template import prepare_multiple_sample_news
from rss.elastic import elastic_search_entity, similar_news_to_query
from newsbot.settings import SAMPLE_NEWS_COUNT, MIN_HITS_ENTITY_VALIDATION, DAYS_FOR_SEARCH_NEWS
from telegrambot.bot_send import send_telegram_user, error_text
from newsbot.settings import MAIN_BUTTONS
from telegrambot import command_handler

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


def search_box_result(bot, msg, user, msg_id=None, text=None):

    if not text:
        text = normalize(msg.message.text)
    hits = elastic_search_entity(text, max(MIN_HITS_ENTITY_VALIDATION, SAMPLE_NEWS_COUNT) + 1)

    response = ""

    no_response = False
    elastic_query = '0'
    if hits:
        h_response, h_response_len = prepare_multiple_sample_news(list(map(int, [hit['_id'] for hit in hits])),
                                                                  SAMPLE_NEWS_COUNT)
        if len(hits) >= MIN_HITS_ENTITY_VALIDATION:
            entity = Entity.objects.get_or_create(name=text, wiki_name='')[0]
            response += Emoji.BOOKMARK + \
                        "با انتخاب دسته زیر ، اخبار مرتبط به صورت بر خط برای شما ارسال خواهد شد." + \
                        '\n' + prepare_advice_entity_link(entity) + '\n' + Emoji.HEAVY_MINUS_SIGN * 5 + '\n'
            response += "%s خبرهای مرتبط با دسته فوق:\n" % Emoji.LARGE_RED_CIRCLE + '\n' + h_response

        else:
            no_response = True

    if not hits or no_response:
        elastic_query = '1'
        similar_news_id = similar_news_to_query(text, SAMPLE_NEWS_COUNT, DAYS_FOR_SEARCH_NEWS)
        similar_news = prepare_multiple_sample_news(similar_news_id, 2)[0]

        def print_n_gram(n_gram):
            gram_response = ""
            not_response = True
            for word in n_gram:
                related_hits = elastic_search_entity(word, MIN_HITS_ENTITY_VALIDATION)
                if len(related_hits) >= MIN_HITS_ENTITY_VALIDATION:
                    en = Entity.objects.get_or_create(name=word, wiki_name='')[0]
                    gram_response += prepare_advice_entity_link(en) + '\n'
                    not_response = False

            return not_response, gram_response
        pre_response = Emoji.WARNING_SIGN + "متن وارد شده یافت نشد.\n" + Emoji.BOOKMARK + \
                       "دسته های مشابه پیشنهادی:‌\n با انتخاب هر یک اخبار مرتبط به صورت بر خط برای شما ارسال خواهد شد.\n"

        three_gram = tri_gram(text)
        no_three_gram_response, three_response = print_n_gram(three_gram)
        if no_three_gram_response:
            two_gram = bi_gram(text)
            no_two_gram_response, two_response = print_n_gram(two_gram)
            if no_two_gram_response:
                one_gram = word_tokenize(text)
                no_one_gram_response, one_response = print_n_gram(one_gram)
                if no_one_gram_response:
                    if not similar_news_id:
                        error_text(bot, msg, user, 'InvalidEntity')
                        return
                else:
                    response += pre_response + one_response
            else:
                response += pre_response + two_response
        else:
            response += pre_response + three_response

        response += Emoji.HEAVY_MINUS_SIGN * 5 + '\n' + Emoji.NEWSPAPER + "خبرهای مشابه \n" + similar_news + '\n'

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

    if len(hits) == SAMPLE_NEWS_COUNT:
        keyboard = None

    send_telegram_user(bot, user, response, msg, keyboard, final_destination)


