from django.db import models
from django.utils.translation import ugettext_lazy as _

from .uri_list import URIList


class UserMixin(models.Model):
	class Meta:
		abstract = True

	oauth_app = models.ForeignKey('openid_provider.App', verbose_name = _("application"), null = True, blank = True, related_name = 'service_account_set')

	OAUTH_APPLICATION_TYPES = [
		('web', _("Web application")),
		('native', _("Native application")),
	]

	oauth_application_type = models.CharField(verbose_name = _("application type"), choices = OAUTH_APPLICATION_TYPES, max_length = 50, default = 'web')

	OAUTH_AUTH_METHODS = [
		('none', _("No authentication")),
		('client_secret_basic', _("HTTP Basic authentication")),
		('client_secret_post', _("Client credentials in the request body")),
	]

	oauth_auth_method = models.CharField(verbose_name = _("authentication method"), choices = OAUTH_AUTH_METHODS, max_length = 50, default = 'client_secret_basic')

	oauth_software_id = models.CharField(verbose_name = _("software id"), max_length = 100, blank = True)
	oauth_software_version = models.CharField(verbose_name = _("software version"), max_length = 100, blank = True)

	_oauth_redirect_uris = models.TextField(verbose_name = _("redirect URIs"), help_text = _("Enter each URI on a new line."), blank = True)
	_oauth_post_logout_redirect_uris = models.TextField(verbose_name = _("post-logout redirect URIs"), help_text = _("Enter each URI on a new line."), blank = True)
	oauth_allow_wildcard_redirect = models.BooleanField(verbose_name = _("allow wildcards in redirect URIs"), default = False)

	@property
	def oauth_redirect_uris(self):
		return URIList(self._oauth_redirect_uris.splitlines(), self.oauth_allow_wildcard_redirect)

	@oauth_redirect_uris.setter
	def oauth_redirect_uris(self, value):
		self._oauth_redirect_uris = '\n'.join(value)

	@property
	def oauth_post_logout_redirect_uris(self):
		return URIList(self._oauth_post_logout_redirect_uris.splitlines(), self.oauth_allow_wildcard_redirect)

	@oauth_post_logout_redirect_uris.setter
	def oauth_post_logout_redirect_uris(self, value):
		self._oauth_post_logout_redirect_uris = '\n'.join(value)

	class Admin:
		fieldsets = (
			(_("OAuth / OpenID Connect"), dict(fields = ('oauth_app', 'oauth_application_type', 'oauth_auth_method', '_oauth_redirect_uris', '_oauth_post_logout_redirect_uris', 'oauth_allow_wildcard_redirect', 'oauth_software_id', 'oauth_software_version',))),
		)
