import os
from base64 import urlsafe_b64encode

from .. import jwt
from ..userinfo import makeUserInfo


def oidc_hash(hash, token):
	hashed = hash(token.encode('ascii'))
	return urlsafe_b64encode(hashed[:len(hashed) // 2]).rstrip(b'=').decode('ascii')


def makeIDToken(request, client, user, scope, nonce, at=None, c=None):
	id = makeUserInfo(user, client, scope)

	if False: # TODO There is no request.session['auth_time'].
		id['auth_time'] = int(request.session['auth_time']),

	if nonce:
		id['nonce'] = nonce

	if at:
		id['at_hash'] = oidc_hash(jwt.myself.signing_hash, at)

	if c:
		id['c_hash'] = oidc_hash(jwt.myself.signing_hash, c)

	return jwt.encode(jwt.myself, [client], id, int(os.environ.get('EXPIRE_IDTOKEN', 2*60)))


def expandIDToken(token):
	return jwt.decode(None, [jwt.myself], token)
