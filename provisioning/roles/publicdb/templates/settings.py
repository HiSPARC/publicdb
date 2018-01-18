# {{ ansible_managed }}
# Django settings for publicdb project.

import os.path

dirname = os.path.dirname(__file__)
PUBLICDB_PATH = os.path.join(dirname, '..')

DEBUG = {{ debug }}

ADMINS = (
    ('Kasper van Dam', 'kaspervd@nikhef.nl'),
    ('Arne de Laat', 'arne@delaat.net'),
)
MANAGERS = ADMINS

SERVER_EMAIL = 'info@hisparc.nl'

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
DATASTORE_PATH = '/databases/frome'
TEST_DATASTORE_PATH = os.path.join(PUBLICDB_PATH, 'datastore_test')

# Path of the mounted HiSPARC event summary datastore (ESD) root folder
ESD_PATH = '/srv/publicdb/www/esd'

# Path of the mounted KNMI Lightning data root folder
LGT_PATH = '/databases/knmi_lightning'

# VPN and datastore XML-RPC Proxies
VPN_PROXY = '{{ vpn_proxy }}'
DATASTORE_PROXY = '{{ datastore_proxy }}'

# VPN and datastore host names
VPN_HOST = '{{ vpn_host }}'
DATASTORE_HOST = '{{ datastore_host }}'

RECAPTCHA_ENABLED = {{ recaptcha_enabled }}
RECAPTCHA_PUB_KEY = '{{ recaptcha_pub_key }}'
RECAPTCHA_PRIVATE_KEY = '{{ recaptcha_private_key }}'

# Process data with multiple threads. Default is disabled (False).
# Disable multiprocessing for debugging purposes. When multithreaded
# processing is enabled the traceback doesn't go to the exact location.
USE_MULTIPROCESSING = True

EMAIL_BACKEND = '{{ email_backend }}'
EMAIL_HOST = '{{ email_host }}'
EMAIL_PORT = {{ email_port }}

TIME_ZONE = 'Europe/Amsterdam'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = False

MEDIA_ROOT = '{{ publicdb_media }}'
MEDIA_URL = '{{ media_url }}'

STATIC_ROOT = '{{ publicdb_static }}'
STATIC_URL = '{{ static_url }}'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = '{{ secret_key }}'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
            ],
        },
    },
]

MIDDLEWARE = (
    # 'django.middleware.gzip.GZipMiddleware',
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
    'publicdb.jsparc',
    'publicdb.station_layout',
    'publicdb.default',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
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
        }
    },
}
