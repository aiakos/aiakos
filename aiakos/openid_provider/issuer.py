import os
from hashlib import sha256
from time import time

from Cryptodome.PublicKey.RSA import importKey
from jwkest.jwk import RSAKey as jwk_RSAKey
from jwkest.jws import JWS

from .models import RSAKey


class Issuer:
	def __init__(self, url):
		self.url = url

	@property
	def keys(self):
		keys = []
		for rsakey in RSAKey.objects.all():
			keys.append(jwk_RSAKey(key=importKey(rsakey.key), kid=rsakey.kid))
		if not keys:
			raise Exception("You must add at least one RSA Key.")

		return keys

	def hash(self, s):
		return sha256(s).digest()

	def issue_token(self, payload, aud, expires_in):
		now = int(time())
		payload['iss'] = self.url
		payload['aud'] = str(aud)
		payload['iat'] = int(now)
		payload['exp'] = int(now + expires_in)

		return JWS(payload, alg='RS256').sign_compact(self.keys)

issuer = Issuer('https://' + os.getenv('AIAKOS_HOSTNAME') + '/')
