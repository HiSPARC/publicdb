"""Wrapper for the writer application"""

import sys

sys.path.append('/srv/datastore/code/writer')

import writer

configfile = ('/srv/datastore/config.ini')
writer.writer(configfile)
