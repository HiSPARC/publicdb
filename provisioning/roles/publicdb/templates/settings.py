# {{ ansible_managed }}
# Django settings for publicdb project.

from os import environ, path

import sentry_sdk

from sentry_sdk.integrations.django import DjangoIntegration

dirname = path.dirname(__file__)
PUBLICDB_PATH = path.join(dirname, '..')

DEBUG = False

ADMINS = (
    ('Kasper van Dam', 'kaspervandam@gmail.com'),
    ('Arne de Laat', 'arne@delaat.net'),
    ('Tom Kooij', 'hisparc@tomkooij.nl'),
    ('David Fokkema', 'davidfokkema@icloud.com'),
)
MANAGERS = ADMINS

SERVER_EMAIL = 'Beheer HiSPARC <bhrhispa@nikhef.nl>'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '{{ psql_database_name }}',
        'USER': '{{ psql_user }}',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Path of the mounted HiSPARC datastore root folder
DATASTORE_PATH = '{{ datastore_data_path }}'
TEST_DATASTORE_PATH = path.join(PUBLICDB_PATH, 'datastore_test')

# Path of the mounted HiSPARC event summary datastore (ESD) root folder
ESD_PATH = '{{ esd_path }}'

# Path of the mounted KNMI Lightning data root folder
LGT_PATH = '{{ lgt_path }}'

# Datastore XML-RPC Proxy
DATASTORE_PROXY = '{{ datastore_proxy }}'

# Datastore host name
DATASTORE_HOST = '{{ datastore_host }}'

# Configure HiSPARC public database url for SAPPHiRE
environ['PUBLICDB_BASE'] = 'http://{{ publicdb_host }}'

# Process data with multiple threads. Default is enabled (True).
# Disable multiprocessing for debugging purposes. When multithreaded
# processing is enabled the traceback doesn't go to the exact location.
USE_MULTIPROCESSING = True

EMAIL_BACKEND = '{{ email_backend }}'
EMAIL_HOST = '{{ email_host }}'
EMAIL_PORT = {{ email_port }}

TIME_ZONE = 'US/Mountain'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = False

MEDIA_ROOT = '{{ publicdb_media }}'
MEDIA_URL = '{{ media_url }}'

STATIC_ROOT = '{{ publicdb_static }}'
STATIC_URL = '{{ static_url }}'

SECRET_KEY = '{{ secret_key }}'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r'^(?!admin/).*']

FILE_UPLOAD_PERMISSIONS = 0o644

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'publicdb.urls'

ALLOWED_HOSTS = [
    '{{ publicdb_host }}',
]

if DEBUG:
    ALLOWED_HOSTS += [
        '127.0.0.1',
        'localhost',
        '[::1]',
    ]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'publicdb.inforecords',
    'publicdb.histograms',
    'publicdb.coincidences',
    'publicdb.status_display',
    'publicdb.analysissessions',
    'publicdb.updates',
    'publicdb.raw_data',
    'publicdb.api',
    'publicdb.maps',
    'publicdb.station_layout',
    'publicdb.default',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(levelname)s - [%(process)d] - %(module)s - %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'},
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'null_handler': {
            'class': 'logging.NullHandler',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '{{ publicdb_logs }}/hisparc-update.log',
            'formatter': 'verbose',
        },
        'file2': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '{{ publicdb_logs }}/hisparc-django-errors.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'file2'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security.DisallowedHost': {
            'handlers': ['null_handler'],
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['null_handler'],
            'propagate': False,
        },
        'publicdb.histograms.management.commands.updatehistograms': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'publicdb.histograms.checks': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'publicdb.histograms.jobs': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

sentry_sdk.init(
    dsn='https://806a6e3a260f422f861fa7d418a2090e@o164994.ingest.sentry.io/1235692',
    integrations=[DjangoIntegration()],
    traces_sample_rate=0,
)
