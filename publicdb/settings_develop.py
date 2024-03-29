# Django settings for publicdb project.

import os.path

BASE_PATH = os.path.dirname(__file__)
PUBLICDB_PATH = os.path.join(BASE_PATH, '..')

DEBUG = True

ADMINS = ()

MANAGERS = ADMINS

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'publicdb',
        'USER': 'hisparc',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    },
}

# Path of the mounted HiSPARC datastore root folder
DATASTORE_PATH = os.path.join(PUBLICDB_PATH, 'datastore')
TEST_DATASTORE_PATH = os.path.join(PUBLICDB_PATH, 'datastore_test')

# Path of the mounted HiSPARC event summary datastore (ESD) root folder
ESD_PATH = os.path.join(PUBLICDB_PATH, 'esd')

# Path of the mounted KNMI Lightning data root folder
LGT_PATH = os.path.join(PUBLICDB_PATH, 'knmi_lightning')

# Datastore XML-RPC Proxy
# This is None in tests/development to disable attempts at connections
DATASTORE_PROXY = None  # 'http://localhost:8002'

# Datastore host name
DATASTORE_HOST = 'localhost'

# Process data with multiple threads. Default is enabled (True).
# Disable multiprocessing for debugging purposes. When multithreaded
# processing is enabled the traceback doesn't go to the exact location.
USE_MULTIPROCESSING = False

# Disable emailing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

TIME_ZONE = 'Europe/Amsterdam'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = False

MEDIA_ROOT = os.path.join(PUBLICDB_PATH, 'mediaroot/')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PUBLICDB_PATH, 'staticroot/')
STATIC_URL = '/static/'

SECRET_KEY = 'Make-this-unique-and-do-not-share-it-with-anybody'

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
    'data.hisparc.nl',
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
    'filters': {'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'}},
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'null_handler': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
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
        'publicdb': {
            'handlers': ['null_handler'],
            'propagate': False,
        },
    },
}
