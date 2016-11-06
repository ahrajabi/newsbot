import locale
import jdatetime
from datetime import datetime
from telegram.emoji import Emoji
from django.conf import settings
from django.utils import timezone
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from rss.models import News
from rss.models import ImageUrls
from rss.news import is_liked_news
from newsbot.settings import BOT_NAME
from entities.models import NewsEntity
from rss.elastic import more_like_this
from telegrambot.models import UserNews
from rss.ml import normalize, sent_tokenize
from telegrambot.bot_send import send_telegram_user


def georgian_to_jalali(datetime):
    jal = jdatetime.GregorianToJalali(datetime.year, datetime.month, datetime.day)
    locale.setlocale(locale.LC_ALL, "fa_IR")
    ret = jdatetime.datetime(jal.jyear, jal.jmonth, jal.jday).strftime("%a, %d %b") + ' ' + \
          timezone.localtime(datetime).strftime("%M:%-H")
    return normalize(ret)


def to_iran_date_time(date_time):
    jal_date = jdatetime.GregorianToJalali(date_time.year, date_time.month, date_time.day)
    local_time = timezone.localtime(date_time)
    return datetime(jal_date.jyear, jal_date.jmonth, jal_date.jday, local_time.hour, local_time.minute, local_time.second)


def now_time_difference(date_time):
    now = to_iran_date_time(timezone.now())
    local_date_time = to_iran_date_time(date_time)

    diff = now - local_date_time

    if diff.days >= 7:
        return date_time, 'dt'
    elif 0 < diff.days < 7:
        if local_date_time.time() > now.time():
            return diff.days + 1, 'd'
        else:
            return diff.days, 'd'
    else:
        if diff.seconds < 60:
            return diff.seconds, 's'
        elif 60 <= diff.seconds < 3600:
            return int(diff.seconds / 60), 'm'
        else:
            return int(diff.seconds / 3600), 'h'


def prepare_time(date_time):
    diff, diff_type = now_time_difference(date_time)
    if diff_type == 'dt':
        return georgian_to_jalali(date_time)
    elif diff_type == 'd':
        return str(diff) + 'روز پیش'
    elif diff_type == 'h':
        return str(diff) + 'ساعت پیش'
    elif diff_type == 'm':
        return str(diff) + 'دقیقه پیش'
    elif diff_type == 's':
        return str(diff) + 'ثانیه پیش'


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
        text = Emoji.PUBLIC_ADDRESS_LOUDSPEAKER + title
    # text += '    ' + Emoji.SMALL_BLUE_DIAMOND + news.get_summary() + '\n'
    try:
        # text += '    ' + Emoji.WHITE_HEAVY_CHECK_MARK + 'منبع:‌ ' + source + '\n'
        text += ' (%s) \n' %source
    except Exception:
        pass
    text += '    ' + Emoji.CALENDAR + ' ' + prepare_time(news.base_news.published_date) + '\n'
    if not inline:
        text += '    ' + Emoji.NEWSPAPER + 'مشاهده خبر:' + '/News_' + str(news.id) + '\n'
    else:
        #https://telegram.me/chvotebot?start=f9830f23b29d139df0377496211a599b9eddeb5e2eb75ce71e12
        text += '    ' + Emoji.NEWSPAPER+\
                '<a href=' +'"https://telegram.me/'+settings.BOT_NAME[1:]+'?start=' +'N' + str(news.id) +'">' + 'مشاهده‌ی سریع خبر' + '</a>\n'

    return text + '\n'


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

    return text, news_count


# def publish_sample_news(bot, msg, news_id_list, total_news, keyboard=None):
#     text = "%s خبرهای مرتبط:\n" % Emoji.NEWSPAPER
#     text += prepare_multiple_sample_news(news_id_list, total_news)
#     send_telegram(bot, msg, text, keyboard=None)


def news_image_page(bot, news, user=None, page=1, message_id=None, picture_number=0):
    # TODO fix not found image urls
    image_url = ImageUrls.objects.filter(news=news)
    if image_url:
        image_url = image_url[picture_number].img_url
    else:
        image_url = settings.TELEGRAM_LOGO

    if user:
        UserNews.objects.update_or_create(user=user, news=news, defaults={'image_page': page})

    text = "<a href= '%s'>''</a>" % image_url
    return text


def news_page(bot, news, user, page=1, message_id=None, picture_number=0, **kwargs):
    like = InlineKeyboardButton(text=Emoji.THUMBS_UP_SIGN + "(" + normalize(str(news.like_count)) + ")",
                                callback_data='news-' + str(news.id) + '-like-' + str(picture_number))

    if is_liked_news(news=news, user=user):
        like = InlineKeyboardButton(text=Emoji.THUMBS_DOWN_SIGN + "(" + normalize(str(news.like_count)) + ")",
                                    callback_data='news-' + str(news.id) + '-unlike-' + str(picture_number))

    buttons = [
        [
            InlineKeyboardButton(text='متن کامل خبر', callback_data='news-' + str(news.id) + '-full-' +
                                                                    str(picture_number)),
            InlineKeyboardButton(text='خلاصه', callback_data='news-' + str(news.id) + '-overview-' + str(picture_number)),
                     ],
        [
            InlineKeyboardButton(text='اخبار مرتبط', callback_data='news-' + str(news.id) + '-stat-' +
                                                                   str(picture_number)),
            like,
        ], ]
    if news.pic_number > 1 and page == 1:
        if picture_number < news.pic_number - 1:
            buttons[0].append(
                InlineKeyboardButton(text='عکس بعدی', callback_data='news-' + str(news.id) + '-img-' +
                                                                    str(picture_number)),
            )
        elif picture_number == news.pic_number - 1:
            buttons[0].append(
                InlineKeyboardButton(text='عکس اول', callback_data='news-' + str(news.id) + '-img' +
                                     str(picture_number)),
            )

    keyboard = InlineKeyboardMarkup(buttons)
    text = ''
    if page == 1:
        del buttons[0][1]
        try:
            text += news_image_page(bot, news, user, page=1, message_id=message_id, picture_number=picture_number)
        except Exception:
            print(Exception)

        summary = news.summary
        has_summary = True

        if not summary:
            summary = news.body[:500]
            has_summary = False

        text += Emoji.PUBLIC_ADDRESS_LOUDSPEAKER + news.base_news.title + '\n\n'

        for sentence in sent_tokenize(summary):
            text += '    ' + Emoji.SMALL_BLUE_DIAMOND + sentence + '\n'
            if len(text) > 300 and not has_summary:
                break
        try:
            text += '    ' + Emoji.CALENDAR + ' ' + georgian_to_jalali(news.base_news.published_date) + '\n'
            text += '    ' + Emoji.WHITE_HEAVY_CHECK_MARK + 'منبع:‌ '
            text += "<a href= '%s'> %s \n</a>" % (news.base_news.url, news.base_news.rss.news_agency.fa_name)
        except Exception:
            pass

        if 'user_entity' in kwargs:
            news_user_entity = NewsEntity.objects.filter(news=news, entity__in=kwargs['user_entity'])
            if news_user_entity:
                text += '\n' + Emoji.BOOKMARK + ' دسته های مشترک با علاقه مندی شما:\n'
                for en in news_user_entity:
                    text += en.entity.name + ', '
                text += '\n'

    elif page == 2:
        del buttons[0][0]
        try:
            text += Emoji.PUBLIC_ADDRESS_LOUDSPEAKER + news.base_news.title + '\n\n    '
        except Exception:
            pass

        if len(news.body) < 3500:
            text += news.body + '\n'
        else:
            text += news.body[:3500].rsplit(' ', 1)[0]
            text += '\n' + 'ادامه دارد...' + '\n'
    elif page == 3:
        related = more_like_this(news.base_news.title, 5)
        text, notext = prepare_multiple_sample_news(related, 5)

    send_telegram_user(bot, user, text, keyboard=keyboard, message_id=message_id)
    UserNews.objects.update_or_create(user=user, news=news, defaults={'page': page})


def inline_news_page(bot, news, page=1, message_id=None, picture_number=0, **kwargs):
    like = InlineKeyboardButton(text=Emoji.THUMBS_UP_SIGN + "(" + normalize(str(news.like_count)) + ")",
                                callback_data='news-' + str(news.id) + '-like-' + str(picture_number))

    # if is_liked_news(news=news, user=user):
    #     like = InlineKeyboardButton(text=Emoji.THUMBS_DOWN_SIGN + "(" + normalize(str(news.like_count)) + ")",
    #                                 callback_data='news-' + str(news.id) + '-unlike-' + str(picture_number))

    buttons = [
        [
            InlineKeyboardButton(text='متن کامل خبر', callback_data='news-' + str(news.id) + '-full-' +
                                                                    str(picture_number)),
            InlineKeyboardButton(text='خلاصه',
                                 callback_data='news-' + str(news.id) + '-overview-' + str(picture_number)),
        ],
        [
            InlineKeyboardButton(text='اخبار مرتبط', callback_data='news-' + str(news.id) + '-stat-' +
                                                                   str(picture_number)),
            like,
        ], ]
    if news.pic_number > 1 and page == 1:
        if picture_number < news.pic_number - 1:
            buttons[0].append(
                InlineKeyboardButton(text='عکس بعدی', callback_data='news-' + str(news.id) + '-img-' +
                                                                    str(picture_number)),
            )
        elif picture_number == news.pic_number - 1:
            buttons[0].append(
                InlineKeyboardButton(text='عکس اول', callback_data='news-' + str(news.id) + '-img' +
                                                                   str(picture_number)),
            )

    keyboard = InlineKeyboardMarkup(buttons)
    text = ''
    if page == 1:
        try:
            text += news_image_page(bot, news, page=1, message_id=message_id, picture_number=picture_number)
        except Exception:
            print(Exception)

        summary = news.summary
        has_summary = True

        if not summary:
            summary = news.body[:500]
            has_summary = False

        text += Emoji.PUBLIC_ADDRESS_LOUDSPEAKER + news.base_news.title + '\n\n'

        for sentence in sent_tokenize(summary):
            text += '    ' + Emoji.SMALL_BLUE_DIAMOND + sentence + '\n'
            if len(text) > 300 and not has_summary:
                break
        try:
            text += '    ' + Emoji.CALENDAR + ' ' + georgian_to_jalali(news.base_news.published_date) + '\n'
            text += '    ' + Emoji.PUBLIC_ADDRESS_LOUDSPEAKER + \
                    '<a href=' + '"https://telegram.me/' + settings.BOT_NAME[1:] + '?start=' + 'N' + str(
                news.id) + '">' + 'مشاهده‌ی سریع خبر' + '</a>\n'

            text += "<a href= '%s'> %s \n</a>" % (news.base_news.url, news.base_news.rss.news_agency.fa_name)
        except Exception:
            pass

        if 'user_entity' in kwargs:
            news_user_entity = NewsEntity.objects.filter(news=news, entity__in=kwargs['user_entity'])
            if news_user_entity:
                text += '\n' + Emoji.BOOKMARK + ' دسته های مشترک با علاقه مندی شما:\n'
                for en in news_user_entity:
                    text += en.entity.name + ', '
                text += '\n'

    elif page == 2:
        try:
            text += Emoji.PUBLIC_ADDRESS_LOUDSPEAKER + news.base_news.title + '\n\n    '
        except Exception:
            pass

        if len(news.body) < 3500:
            text += news.body + '\n'
        else:
            text += news.body[:3500].rsplit(' ', 1)[0]
            text += '\n' + 'ادامه دارد...' + '\n'
    elif page == 3:
        related = more_like_this(news.base_news.title, 5)
        text, notext = prepare_multiple_sample_news(related, 5)

    return text, keyboard
