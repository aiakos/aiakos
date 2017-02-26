from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .client import Client


class UserConsent(models.Model):
	class Meta:
		verbose_name = _("user consent")
		verbose_name_plural = _("user consents")
		unique_together = ('user', 'client')

	user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"))
	client = models.ForeignKey(Client, verbose_name=_("client"))
	_scope = models.TextField(default='', verbose_name=_("scopes"))

	date_given = models.DateTimeField(verbose_name=_("date given"), auto_now_add=True)
	date_updated = models.DateTimeField(verbose_name=_("date updated"), auto_now=True)

	@property
	def scope(self):
		return set(self._scope.split())

	@scope.setter
	def scope(self, value):
		self._scope = ' '.join(value)

	def __str__(self):
		return '{0} - {1}'.format(self.client, self.user)
