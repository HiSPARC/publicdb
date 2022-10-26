""" Simple XML-RPC Client to test VPN server response

    This client can be used to test the VPN XML-RPC server.

"""
import base64

from xmlrpc.client import ServerProxy

vpn_server = ServerProxy('http://localhost:8001')
print(vpn_server.system.listMethods())
print(vpn_server.create_key('sciencepark501', 'client', '192.168.0.1'))
print(vpn_server.register_hosts_ip([('nikhef1', '192.168.0.1'), ('nikhef2', '192.168.0.2')]))
zip = base64.b64decode(vpn_server.get_key('sciencepark501', 'client').data)
with open('/tmp/test.zip', 'wb') as file:
    file.write(zip)
