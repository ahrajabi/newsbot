from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        # logging.config.dictConfig(settings.LOGGING)
        # logging.setLoggerClass(ColoredLogger)

        from telegrambot import bottask
