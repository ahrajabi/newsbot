ELASTIC_URL = 'http://localhost:9200'
# TELEGRAM_TOKEN = '256460947:AAE3Glgg0-NVC78Cn7J58wsrYyEFzqWGBzA'
TELEGRAM_TOKEN = '221098756:AAHa_e2kadI-4IEtVMOStRTrwmUftK9vWR4'

DATABASES = {
    #     'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # },
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'newsbot',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
    #  'news_db': {
    #    'ENGINE': 'django_mongodb_engine',
    #    'NAME': 'my_database'
    # }
}

TG_CLI = {'telegram': '/home/khabareman/tg/bin/telegram-cli',
          'pubkey_file': '/home/khabareman/tg/tg-serer.pub'}

DEBUG = True
