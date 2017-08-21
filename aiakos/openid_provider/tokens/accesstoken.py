import os

from django.contrib.auth import get_user_model

from .. import jwt

Account = get_user_model()


class AccessToken:
	def __init__(self, data):
		self.__dict__ = data

	@property
	def client(self):
		return Account.objects.get(id=self.azp)

	@property
	def user(self):
		return Account.objects.get(id=self.sub)


def makeAccessToken(client, user, scope, confidential=False):
	data = dict(
		azp = str(client.id),
		sub = str(user.id),
		scope = list(scope),
		confidential = confidential,
	)
	expires_in = int(os.environ.get('EXPIRE_ACCESS_TOKEN', 10*60))
	return 'Bearer', jwt.encode(jwt.myself, [jwt.myself], data, expires_in), expires_in


def expandAccessToken(token):
	return AccessToken(jwt.decode(jwt.myself, [jwt.myself], token))
