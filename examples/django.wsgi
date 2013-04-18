import os
import sys

sys.path.append('/vagrant')
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_publicdb.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
