import os
import sys

sys.path.append('/user/admhispa/http/pique')
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_publicdb.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
