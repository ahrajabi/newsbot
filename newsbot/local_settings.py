TELEGRAM_TOKEN = '221098756:AAHa_e2kadI-4IEtVMOStRTrwmUftK9vWR4'
DEBUG = True
CELERY_WORKER_NUM = 6
CELERYD_CONCURRENCY = 5

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'newsbot',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'newsbot_db',
    #     'USER': 'postgres',
    #     'PASSWORD': 'hbCSrLS4MztknYnhMnBS',
    #     'HOST': 'soor.ir',
    #     'PORT': '',
    # },

    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'newsbot_db',
    #     'USER': 'postgres',
    #     'PASSWORD': 'hbCSrLS4MztknYnhMnBS',
    #     'HOST': 'khabareman.com',
    #     'PORT': '5432',
    # },
}

ELASTIC_URL = 'http://localhost:9200'