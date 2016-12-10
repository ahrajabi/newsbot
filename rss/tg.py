from django.core.files import File
from django.utils import timezone
from rss.models import News, NewsAgency, BaseNews, TelegramPost, BadNews
from pytg import Telegram
from datetime import datetime
from django.conf import settings
from pytg.exceptions import NoResponse

tg = Telegram(
    telegram=settings.TG_CLI['telegram'],
    pubkey_file=settings.TG_CLI['pubkey_file']
)


def telegram_crawler():
    receiver = tg.receiver
    sender = tg.sender

    receiver.start()
    main_loop(sender)
    receiver.stop()


def main_loop(sender):
    try:
        channel_list = sender.channel_list()
    except NoResponse:
        return
    for channel in channel_list:
        print(channel['title'])
        try:
            history = sender.history(channel['id'], 5)
        except NoResponse:
            continue

        for msg in history:
            try:
                reply_to = TelegramPost.objects.get(id=msg['reply_id'])
            except KeyError:
                reply_to = None
            except TelegramPost.DoesNotExist:
                reply_to = None

            if not msg.event == 'message':
                continue
            if not msg['from']['id'] == channel['id']:
                continue

            obj, created = TelegramPost.objects.get_or_create(id=msg['id'], channel_id=channel['id'],
                                                              defaults={'reply_to': reply_to})
            if not created:
                continue

            image_file = None
            file = None

            if hasattr(msg, 'media'):
                if msg.media.type == 'photo':
                    image_file = File(open(sender.load_photo(msg.id), 'rb'))
                elif msg.media.type == 'audio':
                    continue
                    # file = File(open(sender.load_audio(msg.id), 'rb'))

                elif msg.media.type == 'file':
                    continue
                    # file = File(open(sender.load_file(msg.id), 'rb'))

                elif msg.media.type == 'document':
                    continue
                    # file = File(open(sender.load_document(msg.id), 'rb'))

                elif msg.media.type == 'video':
                    continue
                    # file = File(open(sender.load_video(msg.id), 'rb'))

            try:
                text = msg.text
            except AttributeError:
                text = msg.media.caption

            news_agency, created = NewsAgency.objects.get_or_create(name=channel['id'],
                                                                    defaults={'fa_name': channel['title'],
                                                                              'url': 'http://telegram.me'})

            title = "پست تلگرام"
            body = text

            if find_advertisement(body):
                model = BadNews
            else:
                model = News

            obj_base = BaseNews.objects.create(title=title,
                                               news_agency=news_agency,
                                               published_date=timezone.make_aware(datetime.fromtimestamp(msg.date)),
                                               source_type=3)

            news = model.objects.create(base_news=obj_base,
                                        body=body,
                                        pic_number=0,
                                        summary=body,
                                        photo=image_file,
                                        file=file)

            obj_base.complete_news = True
            obj_base.save()
            obj.news = news
            obj.save()


def find_advertisement(text):
    if 'telegram.me/joinchat/' in text:
        return 1
    else:
        return 0
