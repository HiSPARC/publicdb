# Django settings for when running publicdb via docker-compose.

from .settings_develop import *  # noqa: F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'publicdb',
        'USER': 'hisparc',
        'PASSWORD': 'postgres',
        'HOST': 'postgres',
        'PORT': '5432',
    },
}

ALLOWED_HOSTS += [
    'publicdb',
]

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Datastore XML-RPC Proxy
# This is None in tests/development to disable attempts at connections
DATASTORE_PROXY = 'http://datastore:8002'

# Datastore host name
DATASTORE_HOST = 'publicdb_datastore_1.publicdb_default'
