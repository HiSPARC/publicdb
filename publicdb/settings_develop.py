# Django settings for publicdb project.

import os.path

BASE_PATH = os.path.dirname(__file__)
PUBLICDB_PATH = os.path.join(BASE_PATH, '..')

DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'publicdb',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Path of the mounted HiSPARC datastore root folder
DATASTORE_PATH = os.path.join(PUBLICDB_PATH, 'datastore')
TEST_DATASTORE_PATH = os.path.join(PUBLICDB_PATH, 'datastore_test')

# Path of the mounted HiSPARC event summary datastore (ESD) root folder
ESD_PATH = os.path.join(PUBLICDB_PATH, 'esd')

# Path of the mounted KNMI Lightning data root folder
LGT_PATH = os.path.join(PUBLICDB_PATH, 'knmi_lightning')

# VPN and datastore XML-RPC Proxies
VPN_PROXY = 'http://localhost:8001'
DATASTORE_PROXY = 'http://localhost:8002'

# VPN and datastore host names
VPN_HOST = 'localhost'
DATASTORE_HOST = 'localhost'

# Webserver of the publicdb where Nagios will retrieve active check results
PUBLICDB_HOST_FOR_NAGIOS = 'http://data.hisparc.nl'

# reCAPTCHA settings
RECAPTCHA_ENABLED = False
RECAPTCHA_PUB_KEY = 'foobar'
RECAPTCHA_PRIVATE_KEY = 'foobaz'

# Process data with multiple threads. Default is disabled (False).
# Disable multiprocessing for debugging purposes. When multithreaded
# processing is enabled the traceback doesn't go to the exact location.
USE_MULTIPROCESSING = False

# Disable emailing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

TIME_ZONE = 'Europe/Amsterdam'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = False

MEDIA_ROOT = os.path.join(PUBLICDB_PATH, '/mediaroot/')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PUBLICDB_PATH, '/staticroot/')
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = 'Make-this-unique-and-do-not-share-it-with-anybody'

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
