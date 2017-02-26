import os
from datetime import timedelta

from django.db import models
from django.utils import timezone

from ._sql import SQLBaseModel


class AccessToken(SQLBaseModel):
	confidential = models.BooleanField()


def makeAccessToken(client, user, scope, confidential=False):
	expires_in = int(os.environ.get('EXPIRE_ACCESS_TOKEN', 10*60))
	token = AccessToken.objects.create(client=client, user=user, scope=scope, confidential=confidential, expires_at=timezone.now() + timedelta(seconds=expires_in))
	return 'Bearer', str(token.id), expires_in


def expandAccessToken(code):
	try:
		return AccessToken.objects.get(id=code)
	except AccessToken.DoesNotExist:
		raise ValueError()
