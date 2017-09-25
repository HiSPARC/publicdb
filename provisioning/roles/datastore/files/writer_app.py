"""Wrapper for the writer application"""

import sys

sys.path.append('/srv/datastore/code')

from writer import writer_app

configfile = ('/srv/datastore/config.ini')
writer_app.writer(configfile)
