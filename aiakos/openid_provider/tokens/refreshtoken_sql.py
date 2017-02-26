import os
from datetime import timedelta

from django.utils import timezone

from ._sql import SQLBaseModel


class RefreshToken(SQLBaseModel):
	pass


def makeRefreshToken(client, user, scope):
	expires_in = int(os.environ.get('EXPIRE_REFRESH_TOKEN', 10*24*60*60))
	token = RefreshToken.objects.create(client=client, user=user, scope=scope, expires_at=timezone.now() + timedelta(seconds=expires_in))
	return str(token.id)


def expandRefreshToken(token):
	try:
		return RefreshToken.objects.get(id=token)
	except RefreshToken:
		raise ValueError()
