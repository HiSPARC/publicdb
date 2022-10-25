#!/usr/bin/python
""" Simple XML-RPC Server to run on the datastore server.

    This daemon should be run on HiSPARC's datastore server.  It will
    handle the cluster layouts and station passwords.  When an update is
    necessary, it will reload the HTTP daemon.

    The basis for this code was ripped from the python SimpleXMLRPCServer
    library documentation and extended.

"""
import hashlib

from urllib.request import urlopen
from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer

HASH = '/tmp/hash_datastore'
DATASTORE_CFG = '/tmp/station_list.csv'
CFG_URL = 'http://publicdb:8000/config/datastore'


def reload_datastore():
    """Load datastore config and reload datastore, if necessary"""

    datastore_cfg = urlopen(CFG_URL).read()
    new_hash = hashlib.sha1(datastore_cfg).hexdigest()

    try:
        with open(HASH) as file:
            old_hash = file.readline()
    except OSError:
        old_hash = None

    if new_hash == old_hash:
        print("New hash is old hash")
        return True
    else:
        with open(DATASTORE_CFG, 'w') as file:
            file.write(datastore_cfg)

        print("New hash received")

        with open(HASH, 'w') as file:
            file.write(new_hash)

    return True


class RequestHandler(SimpleXMLRPCRequestHandler):
    # Restrict to a particular path.
    rpc_paths = ('/RPC2',)


if __name__ == '__main__':
    # Create server
    server = SimpleXMLRPCServer(("0.0.0.0", 8002), requestHandler=RequestHandler)
    server.register_introspection_functions()

    server.register_function(reload_datastore)

    # Run the server's main loop
    server.serve_forever()
