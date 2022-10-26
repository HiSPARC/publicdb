#!/usr/bin/python
""" Simple XML-RPC Server to run on the VPN server

    This daemon should be run on HiSPARC's VPN server.  It will handle the
    creation of hosts and keys and the retrieval of HiSPARC certificates.

    The basis for this code was ripped from the python SimpleXMLRPCServer
    library documentation and extended.

"""
import base64

from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer

HOSTS_FILE = '/tmp/hosts-hisparc'


def create_key(host, type, ip):
    """create keys for a host and set up openvpn"""

    if type == 'client':
        print("create key Type was client")
    elif type == 'admin':
        print("create key Type was admin")
    else:
        print("Unexpected key {type=}")
        # raise ValueError(f'Unsupported type; {type}')

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
        print("Unexpected key {type=}")
        # raise ValueError(f'Unsupported type; {type}')

    return base64.b64encode(b'test')


class RequestHandler(SimpleXMLRPCRequestHandler):
    # Restrict to a particular path.
    rpc_paths = ('/RPC2',)


if __name__ == '__main__':
    # Create server
    server = SimpleXMLRPCServer(("0.0.0.0", 8001), requestHandler=RequestHandler)
    server.register_introspection_functions()

    server.register_function(create_key)
    server.register_function(register_hosts_ip)
    server.register_function(get_key)

    # Run the server's main loop
    server.serve_forever()
