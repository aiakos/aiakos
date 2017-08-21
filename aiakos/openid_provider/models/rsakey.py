from django.db import models
from django.utils.translation import ugettext_lazy as _

from jose.jwk import RSAKey as JWK


class RSAKey(models.Model):
	class Meta:
		verbose_name = _("RSA key")
		verbose_name_plural = _("RSA keys")

	key = models.TextField(verbose_name=_("key"), help_text=_("Paste your private RSA Key here."))

	def __str__(self):
		return str(self.id)

	@property
	def kid(self):
		return str(self.id)

	@property
	def public_jwk(self):
		jwk = JWK(self.key, 'RS256').public_key().to_dict()
		jwk['use'] = 'sig'
		jwk['kid'] = self.kid
		return jwk
