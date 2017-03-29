# {{ ansible_managed }}
# Django settings for django_publicdb project.

import os.path

dirname = os.path.dirname(__file__)
publicdb_path = os.path.join(dirname, '..')

DEBUG = {{ debug }}
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Kasper van Dam', 'kaspervd@nikhef.nl'),
    ('Arne de Laat', 'adelaat@nikhef.nl'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '{{ psql_database_name }}',
        'TEST_NAME': os.path.join(publicdb_path, 'public_test.db'),
        'USER': '{{ psql_user }}',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

## Path settings

# Path of the mounted HiSPARC datastore root folder
DATASTORE_PATH = '/databases/frome'
TEST_DATASTORE_PATH = os.path.join(publicdb_path, 'datastore_test')

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

# reCAPTCHA settings
RECAPTCHA_ENABLED = {{ recaptcha_enabled }}
RECAPTCHA_PUB_KEY = '{{ recaptcha_pub_key }}'
RECAPTCHA_PRIVATE_KEY = '{{ recaptcha_private_key }}'

# Process data with multiple threads. Default is disabled (False).
# Disable multiprocessing for debugging purposes. When multithreaded
# processing is enabled the traceback doesn't go to the exact location.
# Also, sqlite3 is single threaded. So when multi processing is used
# together with sqlite3, you might get the message "database is locked".

USE_MULTIPROCESSING = True

# E-mail settings
EMAIL_BACKEND = '{{ email_backend }}'
EMAIL_HOST = '{{ email_host }}'
EMAIL_PORT = {{ email_port }}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
# DEV_ONLY
MEDIA_ROOT = '/srv/publicdb/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '{{ media_url }}'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/srv/publicdb/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '{{ static_url }}'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
# DEV_ONLY
SECRET_KEY = '{{ secret_key }}'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    # 'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django_publicdb.middleware.threadlocals.ThreadLocals',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'django_publicdb.urls'

ALLOWED_HOSTS = [
    'data.hisparc.nl',
]

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django_publicdb.inforecords',
    'django_publicdb.voorraad',
    'django_publicdb.histograms',
    'django_publicdb.coincidences',
    'django_publicdb.status_display',
    'django_publicdb.analysissessions',
    'django_publicdb.updates',
    'django_publicdb.raw_data',
    'django_publicdb.api',
    'django_publicdb.maps',
    'django_publicdb.jsparc',
    'django_publicdb.station_layout',
    'django_publicdb.default',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
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
            'class': 'django.utils.log.NullHandler',
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
