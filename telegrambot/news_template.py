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
from entities.models import NewsEntity
from rss.elastic import more_like_this
from rss.ml import normalize, sent_tokenize
from shortenersite.views import shorten


def georgian_to_jalali(date_time):
    jal = jdatetime.GregorianToJalali(date_time.year, date_time.month, date_time.day)
    locale.setlocale(locale.LC_ALL, "fa_IR")
    ret = jdatetime.datetime(jal.jyear, jal.jmonth, jal.jday).strftime("%a, %d %b") + ' '
    ret += timezone.localtime(date_time).strftime("%M:%-H")
    return normalize(ret)


def to_iran_date_time(date_time):
    jal_date = jdatetime.GregorianToJalali(date_time.year, date_time.month, date_time.day)
    local_time = timezone.localtime(date_time)
    return datetime(jal_date.jyear, jal_date.jmonth, jal_date.jday, local_time.hour, local_time.minute,
                    local_time.second)


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


def sample_news_page(news):
    title = news.base_news.title
    source = news.base_news.news_agency.fa_name
    text = Emoji.PUBLIC_ADDRESS_LOUDSPEAKER + title
    text += ' (%s) \n' % source
    text += '    ' + Emoji.CALENDAR + ' ' + prepare_time(news.base_news.published_date) + '\n'
    text += '    ' + Emoji.NEWSPAPER + 'مشاهده خبر:' + '/News_' + str(news.id) + '\n'

    return text + '\n'


def prepare_multiple_sample_news(news_id_list, total_news):
    # TODO just prepare multiple news"
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


def news_image_page(news, picture_number=0):
    # TODO fix not found image urls
    image_url = ImageUrls.objects.filter(news=news)
    if image_url:
        image_url = image_url[picture_number].img_url
    elif news.photo:
        image_url = settings.SITE_URL + news.photo.url
    else:
        return None
    return image_url


def news_keyboard(news, user=None, page=1, picture_number=0):
    like = InlineKeyboardButton(text=Emoji.THUMBS_UP_SIGN + "(" + normalize(str(news.like_count)) + ")",
                                callback_data='news-' + str(news.id) + '-like-' + str(picture_number))

    if user and is_liked_news(news=news, user=user):
        like = InlineKeyboardButton(text=Emoji.THUMBS_DOWN_SIGN + "(" + normalize(str(news.like_count)) + ")",
                                    callback_data='news-' + str(news.id) + '-unlike-' + str(picture_number))

    full_button = InlineKeyboardButton(text='متن کامل خبر',
                                       callback_data='news-' + str(news.id) + '-full-' + str(picture_number))
    overview_button = InlineKeyboardButton(text='خلاصه',
                                           callback_data='news-' + str(news.id) + '-overview-' + str(picture_number))
    related_button = InlineKeyboardButton(text='اخبار مرتبط',
                                          callback_data='news-' + str(news.id) + '-stat-' + str(picture_number))
    next_image_button = InlineKeyboardButton(text='عکس بعدی', callback_data='news-' + str(news.id) + '-img-' +
                                                                            str(picture_number))
    first_image_button = InlineKeyboardButton(text='عکس اول', callback_data='news-' + str(news.id) + '-img' +
                                                                            str(picture_number))
    image_button = None
    if news.pic_number > 1 and page == 1:
        if picture_number < news.pic_number - 1:
            image_button = next_image_button
        elif picture_number == news.pic_number - 1:
            image_button = first_image_button
    buttons = list()
    keyboard = None
    if page == 1:
        for item in [[full_button, image_button],
                     [related_button, like]]:
            buttons.append([key for key in item if key])
        keyboard = InlineKeyboardMarkup(buttons)
    elif page == 2:
        for item in [[overview_button],
                     [related_button, like]]:
            buttons.append([key for key in item if key])
        keyboard = InlineKeyboardMarkup(buttons)
    elif page == 3:
        for item in [[overview_button, full_button],
                     [related_button, like]]:
            buttons.append([key for key in item if key])
        keyboard = InlineKeyboardMarkup(buttons)
    return keyboard


def news_page(news, page=1, picture_number=0, **kwargs):
    text = ''

    if page == 1:
        image_url = news_image_page(news, picture_number)
        if image_url:
            text += "<a href= '%s'>‌</a>" % image_url + '\n'

        summary = news.summary
        has_summary = True

        if not summary:
            summary = news.body[:500]
            has_summary = False

        if not news.base_news.source_type == 3:
            text += Emoji.PUBLIC_ADDRESS_LOUDSPEAKER + news.base_news.title + '\n\n'
        if not news.base_news.source_type == 3:
            for sentence in sent_tokenize(summary):
                text += '    ' + Emoji.SMALL_BLUE_DIAMOND + sentence + '\n'
                if len(text) > 300 and not has_summary:
                    break
        else:
            text += summary + '\n'
        text += '    ' + Emoji.CALENDAR + ' ' + georgian_to_jalali(news.base_news.published_date) + '\n'
        text += '    ' + Emoji.WHITE_HEAVY_CHECK_MARK + 'منبع:‌ '
        text += "<a href= '%s'> %s </a>" % (shorten(news.base_news.url), news.base_news.news_agency.fa_name)

        if 'user_entity' in kwargs:
            news_user_entity = NewsEntity.objects.filter(news=news, entity__in=kwargs['user_entity'])
            if news_user_entity:
                text += '\n' + Emoji.BOOKMARK + ' دسته های مشترک با علاقه مندی شما:\n'
                for en in news_user_entity:
                    text += en.entity.name + ', '
                text += '\n'
    elif page == 2:
        text += Emoji.PUBLIC_ADDRESS_LOUDSPEAKER + news.base_news.title + '\n\n'

        if len(news.body) < 3400:
            text += news.body + '\n'
            text += news.pdf_link + '\n'
        else:
            text += news.body[:3400].rsplit(' ', 1)[0]
            text += '\n' + 'ادامه دارد...' + '\n'
            text += news.pdf_link + '\n'
    elif page == 3:

        related = more_like_this(news.base_news.title, 5)
        text, no_text = prepare_multiple_sample_news(related, 5)

    return text
