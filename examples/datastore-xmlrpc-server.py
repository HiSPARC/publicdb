#!/usr/bin/python
""" Simple XML-RPC Server to run on the datastore server.

    This daemon should be run on HiSPARC's datastore server.  It will
    handle the cluster layouts and station passwords.  When an update is
    necessary, it will reload the HTTP daemon.

    The basis for this code was ripped from the python SimpleXMLRPCServer
    library documentation and extended.

"""
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import urllib2
import hashlib
import subprocess

HASH = '/tmp/hash_datastore'
DATASTORE_CFG = '/tmp/station_list.csv'
CFG_URL = 'http://data.hisparc.nl/config/datastore'

def reload_datastore():
    """Load datastore config and reload datastore, if necessary"""

    datastore_cfg = urllib2.urlopen(CFG_URL).read()
    new_hash = hashlib.sha1(datastore_cfg).hexdigest()

    try:
        with open(HASH, 'r') as file:
            old_hash = file.readline()
    except IOError:
        old_hash = None

    if new_hash == old_hash:
        return True
    else:
        with open(DATASTORE_CFG, 'w') as file:
            file.write(datastore_cfg)

        subprocess.check_call(['/sbin/service', 'httpd', 'reload'])

        with open(HASH, 'w') as file:
            file.write(new_hash)

    return True


if __name__ == '__main__':
    # Restrict to a particular path.
    class RequestHandler(SimpleXMLRPCRequestHandler):
        rpc_paths = ('/RPC2',)

    # Create server
    server = SimpleXMLRPCServer(("localhost", 8001),
                                requestHandler=RequestHandler)
    server.register_introspection_functions()

    server.register_function(reload_datastore)

    # Run the server's main loop
    server.serve_forever()
