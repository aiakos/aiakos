from hashlib import sha256
from time import time

from django.conf import settings

from jose import jwt

from .models import RSAKey

JWTError = jwt.JWTError


def encode(myself, audience, payload, expires_in):
	now = int(time())
	payload['iss'] = str(myself.id)
	payload['aud'] = [str(a.id) for a in audience]
	payload['iat'] = int(now)
	payload['exp'] = int(now + expires_in)
	signing_key = myself.signing_key

	return jwt.encode(
		payload,
		signing_key.key,
		algorithm = 'RS256',
		headers = dict(
			kid = signing_key.kid,
		),
	)


def decode(myself, issuers, payload):
	# TODO support multiple issuers
	issuer = issuers[0]
	try:
		return jwt.decode(
			payload,
			issuer.public_jwks,
			algorithms = ['RS256'],
			audience = str(myself.id) if myself is not None else None,
			issuer = str(issuer.id),
			options = dict(
				verify_at_hash = False,
				verify_aud = myself is not None,
			),
		)
	except JWTError as e:
		try:
			e.payload = jwt.get_unverified_claims(payload)
		except JWTError:
			pass

		raise


class Myself:
	def __init__(self, id):
		self.id = id

	@property
	def signing_key(self):
		return RSAKey.objects.first()

	@property
	def public_jwks(self):
		return dict(keys=[k.public_jwk for k in RSAKey.objects.all()])

	def signing_hash(self, s):
		return sha256(s).digest()


myself = Myself(settings.BASE_URL)
