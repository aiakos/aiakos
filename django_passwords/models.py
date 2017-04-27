from importlib import import_module
from urllib.parse import urlsplit

from django.db import models
from django.utils.translation import ugettext_lazy as _


class PasswordBackend(models.Model):
	class Meta:
		ordering = ['order']

	order = models.IntegerField(verbose_name=_("order"))
	url = models.URLField(verbose_name=_("URL"))
	copy_passwords_to = models.ForeignKey('self', verbose_name=_("Copy passwords to"), blank=True, null=True)

	@property
	def backend(self):
		scheme = urlsplit(self.url).scheme
		cls = import_module('django_passwords.backends.' + scheme).Backend
		return cls(self.url)

	def __str__(self):
		return "{}. {}".format(self.order, self.url)

	def check_password(self, user, password):
		return self.backend.check_password(user, password)

	def set_password(self, user, password):
		return self.backend.set_password(user, password)
