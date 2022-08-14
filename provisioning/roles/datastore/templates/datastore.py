import sys
import functools

sys.path.append('{{ datastore_code }}')

from wsgi import wsgi_app

configfile = '{{ datastore_path }}config.ini'
application = functools.partial(wsgi_app.application, configfile=configfile)
