import sys
import functools

sys.path.append('/srv/datastore/code/wsgi')

import wsgi_app

configfile = '/srv/datastore/config.ini'
application = functools.partial(wsgi_app.application, configfile=configfile)
