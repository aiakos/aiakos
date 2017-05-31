from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..uri_list import URIList


class Client(models.Model):
	class Meta:
		verbose_name = _("client")
		verbose_name_plural = _("clients")

	user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='openid_client', verbose_name=_("service account"))
	confidential = models.BooleanField(default=True, verbose_name=_("confidential"))
	_redirect_uris = models.TextField(verbose_name=_("redirect URIs"), help_text=_("Enter each URI on a new line."))
	_post_logout_redirect_uris = models.TextField(blank=True, verbose_name=_("post-logout redirect URIs"), help_text=_("Enter each URI on a new line."))
	allow_wildcard_redirect = models.BooleanField(default=False, verbose_name=_("allow wildcards in redirect URIs"))
	_trusted_scopes = models.TextField(default='', verbose_name=_("trusted scopes"), blank=True)

	@property
	def redirect_uris(self):
		return URIList(self._redirect_uris.splitlines(), self.allow_wildcard_redirect)

	@redirect_uris.setter
	def redirect_uris(self, value):
		self._redirect_uris = '\n'.join(value)

	@property
	def post_logout_redirect_uris(self):
		return URIList(self._post_logout_redirect_uris.splitlines(), self.allow_wildcard_redirect)

	@post_logout_redirect_uris.setter
	def post_logout_redirect_uris(self, value):
		self._post_logout_redirect_uris = '\n'.join(value)

	@property
	def trusted_scopes(self):
		return set(self._trusted_scopes.split())

	@trusted_scopes.setter
	def trusted_scopes(self, value):
		self._trusted_scopes = ' '.join(value)

	def __str__(self):
		return str(self.user)
