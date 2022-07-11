#!/usr/bin/python
""" Simple XML-RPC Server to run on the VPN server

    This daemon should be run on HiSPARC's VPN server.  It will handle the
    creation of hosts and keys and the retrieval of HiSPARC certificates.

    The basis for this code was ripped from the python SimpleXMLRPCServer
    library documentation and extended.

"""
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import base64

HOSTS_FILE = '/tmp/hosts-hisparc'


def create_key(host, type, ip):
    """create keys for a host and set up openvpn"""

    if type == 'client':
        print("create key Type was client")
    elif type == 'admin':
        print("create key Type was admin")
    else:
        raise Exception('Unknown type %s' % type)

    return True


def register_hosts_ip(host_list):
    """Register all hosts ips"""

    with open(HOSTS_FILE, 'w') as file:
        for host, ip in host_list:
            file.write(f'{ip}\t{host}.his\n')
            print(f"Writing {ip}, {host} to hosts file")

    return True


def get_key(host, type):
    """Get a zip-archive containing all relevant keys"""

    if type == 'client':
        print("Get key type was client")
    elif type == 'admin':
        print("Get key type was admin")
    else:
        raise Exception('Unknown type %s' % type)

    return base64.b64encode('test')


if __name__ == '__main__':
    # Restrict to a particular path.
    class RequestHandler(SimpleXMLRPCRequestHandler):
        rpc_paths = ('/RPC2',)

    # Create server
    server = SimpleXMLRPCServer(("localhost", 8001),
                                requestHandler=RequestHandler)
    server.register_introspection_functions()

    server.register_function(create_key)
    server.register_function(register_hosts_ip)
    server.register_function(get_key)

    # Run the server's main loop
    server.serve_forever()
