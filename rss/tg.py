from django.core.files import File

from rss.models import News, NewsAgency, BaseNews
from pytg import Telegram
from pytg.utils import coroutine
from datetime import datetime

tg = Telegram(
    telegram="/home/amirhosssein/Downloads/tg/bin/telegram-cli",
    pubkey_file="/home/amirhossein/Downloads/tg/tg-serer.pub"
)


def start():
    receiver = tg.receiver
    sender = tg.sender

    receiver.start()
    receiver.message(main_loop(sender))
    receiver.stop()


@coroutine
def main_loop(sender):
    quit = False
    try:
        while not quit:
            try:
                sender.status_online()
            except:
                pass
            msg = (yield)

            if msg.event == 'online-status':
                continue

            print(msg)

            image_file = None
            file = None

            if hasattr(msg, 'media'):
                print(msg.media.type)
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

            news_agency, created = NewsAgency.objects.get_or_create(name=msg.sender.name,
                                                                    defaults={'fa_name': msg.sender.name,
                                                                              'url': 'http://telegram.me'})

            title = text[0:255]
            body = text
            obj = BaseNews.objects.create(title=title,
                                          news_agency=news_agency,
                                          published_date=datetime.fromtimestamp(msg.date),
                                          source_type=3)

            news = News.objects.create(base_news=obj,
                                       body=body,
                                       pic_number=0,
                                       summary=body,
                                       photo=image_file,
                                       file=file)

            obj.complete_news = True
            obj.save()


    except GeneratorExit:
        # the generator (pytg) exited (got a KeyboardIterrupt).
        pass
    except KeyboardInterrupt:
        # we got a KeyboardIterrupt(Ctrl+C)
        pass
    else:
        # the loop exited without exception, becaues _quit was set True
        pass