from importlib import import_module
from openid_connect import OpenIDClient
import os

def _connect(server, client_id, client_secret, protocol=None):
	if not protocol:
		cls = OpenIDClient
	else:
		cls = import_module('openid_connect.legacy.' + protocol).Client

	return cls(server, client_id, client_secret)

def connect(server, client_id, client_secret, protocol=None, force_protocol=None):
	if force_protocol:
		return _connect(server, client_id, client_secret, force_protocol)

	try:
		return _connect(server, client_id, client_secret)
	except:
		return _connect(server, client_id, client_secret, protocol)

PROTOCOL       = os.environ.get("AUTH_PROTOCOL")
FORCE_PROTOCOL = os.environ.get("AUTH_FORCE_PROTOCOL")
SERVER         = os.environ.get("AUTH_SERVER")
CLIENT_ID      = os.environ.get("AUTH_CLIENT_ID")
CLIENT_SECRET  = os.environ.get("AUTH_CLIENT_SECRET")

if SERVER and CLIENT_ID and CLIENT_SECRET:
	server = connect(SERVER, CLIENT_ID, CLIENT_SECRET, PROTOCOL, FORCE_PROTOCOL)
