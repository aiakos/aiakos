from django.db import models
from django.conf import settings
from openid_connect import OpenIDClient
from openid_connect.legacy import PROTOCOLS
from importlib import import_module
import yaml

PROTOCOL_CHOICES = tuple((protocol, protocol) for protocol in PROTOCOLS)

class IdentityProvider(models.Model):
	name = models.CharField(max_length=200)
	slug = models.SlugField()

	url = models.URLField(max_length=200, verbose_name='URL')
	client_id = models.CharField(max_length=200)
	client_secret = models.CharField(max_length=200)

	legacy_protocol = models.CharField(max_length=50, choices=PROTOCOL_CHOICES, blank=True)
	legacy_settings_yaml = models.TextField(blank=True, verbose_name="Legacy protocol settings", help_text="Legacy protocol specific settings, in YAML. Usually empty.")

	inherit_admin_status = models.BooleanField(default=False, help_text="Grant superuser status to the provider's admins.")

	def __str__(self):
		return self.name

	@property
	def legacy_settings(self):
		if self.legacy_settings_yaml:
			kwargs = yaml.load(self.legacy_settings_yaml)
		else:
			return {}

	@property
	def client(self):
		if not self.legacy_protocol:
			cls = OpenIDClient
		else:
			cls = import_module('openid_connect.legacy.' + self.legacy_protocol).Client

		return cls(self.url, self.client_id, self.client_secret, **self.legacy_settings)

	def save(self, *args, **kwargs):
		self.client
		super().save(*args, **kwargs)

class ExternalIdentity(models.Model):
	class Meta:
		verbose_name_plural = 'External identities'
		unique_together = (('provider', 'sub',),)

	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	provider = models.ForeignKey(IdentityProvider)

	sub = models.CharField(max_length=200)

	userinfo_yaml = models.TextField(default="", verbose_name="User information")

	def __str__(self):
		return '{}@{}'.format(self.sub, self.provider)

	@property
	def userinfo(self):
		try:
			if self._userinfo_yaml == self.userinfo_yaml:
				return self._userinfo
		except AttributeError:
			pass

		self._userinfo_yaml = self.userinfo_yaml
		if self._userinfo_yaml:
			self._userinfo = yaml.load(self.userinfo_yaml)
		else:
			self._userinfo = {}

		return self._userinfo

	@userinfo.setter
	def userinfo(self, v):
		self.userinfo_yaml = yaml.safe_dump(v, default_flow_style=False)
