ELASTIC_URL = 'http://localhost:9200'
TELEGRAM_TOKEN = '256460947:AAE3Glgg0-NVC78Cn7J58wsrYyEFzqWGBzA'

DATABASES = {
    #     'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # },
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'newsbot',
        'USER': 'postgres',
        'PASSWORD': 'asdfjkl;',
        'HOST': 'localhost',
        'PORT': '',
    },
    #  'news_db': {
    #    'ENGINE': 'django_mongodb_engine',
    #    'NAME': 'my_database'
    # }
}

DEBUG = True
