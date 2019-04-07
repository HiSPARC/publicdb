# Django settings for when dunning publicdb via docker-compose.

from .settings_develop import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'publicdb',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'postgres',
        'PORT': '5432',
    }
}

# VPN and datastore XML-RPC Proxies
VPN_PROXY = 'http://vpn:8001'
DATASTORE_PROXY = 'http://datastore:8002'

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
