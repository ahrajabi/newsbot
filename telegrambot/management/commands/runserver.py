from django.core.management import BaseCommand

import atexit
import signal
import sys
from django.conf import settings
from telegrambot.bottask import updater
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.management.commands.runserver import \
    Command as RunserverCommand


# The class must be named Command, and subclass BaseCommand
class Command(RunserverCommand):
    def __init__(self,*args, **kwargs):
        atexit.register(self._exit)
        signal.signal(signal.SIGINT, self._handle_SIGINT)
        super(Command, self).__init__(*args, **kwargs)
    # A command must define handle()

    def _exit(self):
        updater.stop()


    def _handle_SIGINT(self, signal, frame):
        self._exit()
        sys.exit(0)


    help = "Starts a lightweight Web server for development and also serves static files."


    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--nostatic', action="store_false", dest='use_static_handler', default=True,
                            help='Tells Django to NOT automatically serve static files at STATIC_URL.')
        parser.add_argument('--insecure', action="store_true", dest='insecure_serving', default=False,
                            help='Allows serving static files even if DEBUG is False.')


    def get_handler(self, *args, **options):
        """
        Returns the static files serving handler wrapping the default handler,
        if static files should be served. Otherwise just returns the default
        handler.
        """
        handler = super(Command, self).get_handler(*args, **options)
        use_static_handler = options.get('use_static_handler', True)
        insecure_serving = options.get('insecure_serving', False)
        if use_static_handler and (settings.DEBUG or insecure_serving):
            return StaticFilesHandler(handler)
        return handler
