#!/usr/bin/env python
# {{ ansible_managed }}
""" Simple XML-RPC Server to run on the datastore server.

    This daemon should be run on HiSPARC's datastore server.  It will
    handle the cluster layouts and station passwords.  When an update is
    necessary, it will reload the HTTP daemon.

    The basis for this code was ripped from the python SimpleXMLRPCServer
    library documentation and extended.

"""
import hashlib

from pathlib import Path
from urllib.request import urlopen
from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer

HASH = Path('/tmp/hash_datastore')
DATASTORE_CFG = Path('{{ datastore_config }}')
CFG_URL = '{{ datastore_config_url }}'
RELOAD_PATH = Path('/tmp/uwsgi-reload.me')


def reload_datastore():
    """Load datastore config and reload datastore, if necessary"""

    datastore_cfg = urlopen(CFG_URL).read()
    new_hash = hashlib.sha1(datastore_cfg).hexdigest()

    try:
        old_hash = HASH.read_text()
    except OSError:
        old_hash = None

    if new_hash == old_hash:
        return True
    else:
        DATASTORE_CFG.write_bytes(datastore_cfg)

        # reload uWSGI
        Path(RELOAD_PATH).touch()

        HASH.write_text(new_hash)

    return True


class RequestHandler(SimpleXMLRPCRequestHandler):
    # Restrict to a particular path.
    rpc_paths = ('/RPC2',)


if __name__ == '__main__':
    # Create server
    server = SimpleXMLRPCServer(('{{ datastore_host }}', {{datastore_port}}), requestHandler=RequestHandler)
    server.register_introspection_functions()

    server.register_function(reload_datastore)

    # Run the server's main loop
    server.serve_forever()
