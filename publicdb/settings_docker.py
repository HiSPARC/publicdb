# Django settings for when dunning publicdb via docker-compose.

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

# VPN and datastore XML-RPC Proxies
# These are None in tests/development to disable attempts at connections
VPN_PROXY = 'http://vpn:8001'
DATASTORE_PROXY = 'http://datastore:8002'

# VPN and datastore host names
VPN_HOST = 'publicdb_vpn_1.publicdb_default'
DATASTORE_HOST = 'publicdb_datastore_1.publicdb_default'
