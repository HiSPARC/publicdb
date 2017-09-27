"""Wrapper for the writer application"""

import sys

sys.path.append('{{ datastore_code }}')

from writer import writer_app

configfile = ('{{ datastore_path }}config.ini')
writer_app.writer(configfile)
