""" Simple XML-RPC Client to test datastore server response

    This client can be used to test the Datastore XML-RPC server.

"""
import base64

from xmlrpc.client import ServerProxy

datastore_server = ServerProxy('http://localhost:8002')
print(datastore_server.system.listMethods())
print(datastore_server.reload_datastore())
