from django.db import models
from django.utils.translation import ugettext_lazy as _


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
