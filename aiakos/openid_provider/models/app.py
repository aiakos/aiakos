from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..uri_list import URIList


class App(models.Model):
	class Meta:
		verbose_name = _("app")
		verbose_name_plural = _("apps")

	owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name = _("owner"), related_name = 'owned_application_set', null = True, blank = True)

	name = models.CharField(verbose_name = _("name"), max_length = 200, blank = True)
	uri = models.URLField(verbose_name = _("homepage URL"), blank = True)
	initiate_login_uri = models.URLField(verbose_name = _("login initiation URL"), blank = True)
	logo_uri = models.URLField(verbose_name = _("logo URL"), blank = True)
	tos_uri = models.URLField(verbose_name = _("terms of service URL"), blank = True)
	policy_uri = models.URLField(verbose_name = _("privacy policy URL"), blank = True)
	_contacts = models.TextField(verbose_name = _("contact e-mails"), blank = True)

	# sector_identifier_uri
	# subject_type

	_trusted_scopes = models.TextField(verbose_name = _("trusted scopes"), blank = True)

	@property
	def contacts(self):
		return self._contacts.split()

	@contacts.setter
	def contacts(self, value):
		self._contacts = ' '.join(value)

	@property
	def trusted_scopes(self):
		return set(self._trusted_scopes.split())

	@trusted_scopes.setter
	def trusted_scopes(self, value):
		self._trusted_scopes = ' '.join(value)

	def __str__(self):
		return self.name
