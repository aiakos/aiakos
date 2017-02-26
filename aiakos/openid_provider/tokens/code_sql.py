import os
from datetime import timedelta

from django.db import models
from django.utils import timezone

from ._sql import SQLBaseModel


class Code(SQLBaseModel):
	nonce = models.CharField(max_length=255, blank=True, default='')


def makeCode(client, user, scope, nonce=''):
	expires_in = int(os.environ.get('EXPIRE_CODE', 60))
	code = Code.objects.create(client=client, user=user, scope=scope, nonce=nonce, expires_at=timezone.now() + timedelta(seconds=expires_in))
	return str(code.id)


def expandCode(code):
	try:
		code = Code.objects.get(id=code)
		code.delete() # TODO use atomic get-and-delete
		return code
	except Code.DoesNotExist:
		raise ValueError()
