from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Client(models.Model):
	class Meta:
		verbose_name = _("client")
		verbose_name_plural = _("clients")

	user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='openid_client', verbose_name=_("service account"))
	confidential = models.BooleanField(default=True, verbose_name=_("confidential"))
	_redirect_uris = models.TextField(default='', verbose_name=_("redirect URIs"), help_text=_("Enter each URI on a new line."))

	@property
	def redirect_uris(self):
		return self._redirect_uris.splitlines()

	@redirect_uris.setter
	def redirect_uris(self, value):
		self._redirect_uris = '\n'.join(value)

	@property
	def profile(self):
		return self.user.profile

	def __str__(self):
		return str(self.user)
