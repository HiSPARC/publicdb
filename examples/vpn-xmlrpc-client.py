""" Simple XML-RPC Client to test VPN server response

    This client can be used to test the VPN XML-RPC server.

"""
import base64

from xmlrpc.client import ServerProxy

s = ServerProxy('http://localhost:8001')
print(s.system.listMethods())
print(s.create_key('sciencepark501', 'client', '192.168.0.1'))
print(s.register_hosts_ip([('nikhef1', '192.168.0.1'),
                           ('nikhef2', '192.168.0.2')]))
zip = base64.b64decode(s.get_key('sciencepark501', 'client'))
with open('/tmp/test.zip', 'w') as file:
    file.write(zip)
