#!/usr/bin/python
""" Simple XML-RPC Server to run on the VPN server

    This daemon should be run on HiSPARC's VPN server.  It will handle the
    creation of hosts and keys, the reloading of nagios and the retrieval
    of HiSPARC certificates.

    The basis for this code was ripped from the python SimpleXMLRPCServer
    library documentation and extended.

"""
from xmlrpc.serverimport SimpleXMLRPCServer
from xmlrpc.serverimport SimpleXMLRPCRequestHandler
import subprocess
import cStringIO as StringIO
import zipfile
import os
import base64

OPENVPN_DIR = '/home/david/tmp/openvpn'
HOSTS_FILE = '/tmp/hosts-hisparc'
FLAG = '/tmp/flag_nagios_reload'


def create_key(host, type, ip):
    """create keys for a host and set up openvpn"""

    if type == 'client':
        subprocess.check_call(['./create_keys.sh', OPENVPN_DIR, host])
        with open(os.path.join(OPENVPN_DIR, 'ccd', host), 'w') as file:
            file.write('ifconfig-push %s 255.255.254.0\n' % ip)
    elif type == 'admin':
        subprocess.check_call(['./create_admin_keys.sh', OPENVPN_DIR, host])
    else:
        raise Exception('Unknown type %s' % type)

    return True


def register_hosts_ip(host_list):
    """Register all hosts ips"""

    with open(HOSTS_FILE, 'w') as file:
        for host, ip in host_list:
            file.write(f'{ip}\t{host}.his\n')
    subprocess.check_call(['/sbin/service', 'dnsmasq', 'reload'])

    return True


def get_key(host, type):
    """Get a zip-archive containing all relevant keys"""

    memfile = StringIO.StringIO()
    zip_file = zipfile.ZipFile(memfile, 'w')

    if type == 'client':
        key_dir = os.path.join(OPENVPN_DIR, 'keys')
        zip_file.write(f'{key_dir}/{host}.crt', 'hisparc.crt')
        zip_file.write(f'{key_dir}/{host}.key', 'hisparc.key')
        zip_file.write('%s/ca.crt' % key_dir, 'ca.crt')
    elif type == 'admin':
        key_dir = os.path.join(OPENVPN_DIR, 'adminkeys')
        zip_file.write(f'{key_dir}/{host}.crt', 'hisparc_admin.crt')
        zip_file.write(f'{key_dir}/{host}.key', 'hisparc_admin.key')
        zip_file.write('%s/ca.crt' % key_dir, 'ca_admin.crt')
    else:
        raise Exception('Unknown type %s' % type)

    key_dir = os.path.join(OPENVPN_DIR, 'keys')
    zip_file.write('%s/ta.key' % key_dir, 'ta.key')
    zip_file.close()

    zip_file = memfile.getvalue()
    memfile.close()

    return base64.b64encode(zip_file)


def reload_nagios():
    """Signal a reload of nagios"""

    with open(FLAG, 'a') as file:
        pass
    return True


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
    server.register_function(reload_nagios)

    # Run the server's main loop
    server.serve_forever()
