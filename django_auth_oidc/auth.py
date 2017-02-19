from importlib import import_module
import os

def _connect(server, client_id, client_secret, protocol=""):
    if protocol and protocol != "oidc":
        mod_name = protocol
    else:
        mod_name = "django_auth_oidc.oidc"

    mod = import_module(mod_name)

    return mod.AuthorizationServer(server, client_id, client_secret)

def connect(server, client_id, client_secret, protocol="", force_protocol=""):
    if force_protocol:
        return _connect(server, client_id, client_secret, force_protocol)

    try:
        return _connect(server, client_id, client_secret)
    except:
        return _connect(server, client_id, client_secret, protocol)

PROTOCOL       = os.getenv("AUTH_PROTOCOL")
FORCE_PROTOCOL = os.getenv("AUTH_FORCE_PROTOCOL")
SERVER         = os.getenv("AUTH_SERVER")
CLIENT_ID      = os.getenv("AUTH_CLIENT_ID")
CLIENT_SECRET  = os.getenv("AUTH_CLIENT_SECRET")

if SERVER and CLIENT_ID and CLIENT_SECRET:
    server = connect(SERVER, CLIENT_ID, CLIENT_SECRET, PROTOCOL, FORCE_PROTOCOL)
