import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from ..models.client import Client


class SQLBaseModelManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(expires_at__gt=timezone.now())


class SQLBaseModel(models.Model):
	objects = SQLBaseModelManager()

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	client = models.ForeignKey(Client)
	expires_at = models.DateTimeField()
	_scope = models.TextField(default='')

	@property
	def scope(self):
		return set(self._scope.split())

	@scope.setter
	def scope(self, value):
		self._scope = ' '.join(value)

	def __str__(self):
		return '{0} - {1}'.format(self.client, self.user)

	class Meta:
		abstract = True
