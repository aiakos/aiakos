from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from openid_connect import connect
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
		return connect(self.url, self.client_id, self.client_secret, protocol=self.legacy_protocol, **self.legacy_settings)

	def save(self, *args, **kwargs):
		self.client
		super().save(*args, **kwargs)

	@property
	def login_url(self):
		return reverse('extauth:begin', args=[self.slug])

class ExternalIdentity(models.Model):
	class Meta:
		verbose_name_plural = 'External identities'
		unique_together = (('provider', 'sub',),)

	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	provider = models.ForeignKey(IdentityProvider)

	sub = models.CharField(max_length=200)

	userinfo_yaml = models.TextField(default="", verbose_name="User information")

	@property
	def external_name(self):
		try:
			profile = self.profile
		except ImportError:
			pass
		else:
			if profile.nickname:
				return profile.nickname
			if profile.name:
				return profile.name

		return self.sub

	def __str__(self):
		return '{} @ {}'.format(self.external_name, self.provider)

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

	@property
	def profile(self):
		from django_profile_oidc.models import Profile
		return Profile.from_dict(self.userinfo)
