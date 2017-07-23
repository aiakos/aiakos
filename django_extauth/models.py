import random
from importlib import import_module

from django.conf import settings
from django.contrib import auth
from django.db import IntegrityError, models
from django.shortcuts import reverse
from django.utils.translation import ugettext_lazy as _

import yaml
from openid_connect import connect
from openid_connect.legacy import PROTOCOLS

PROTOCOL_CHOICES = (('openid_connect', "OpenID Connect"),) + tuple((protocol, protocol) for protocol in PROTOCOLS)

class IdentityProviderManager(models.Manager):
	def all(self):
		return self.exclude(protocol="")

class IdentityProvider(models.Model):
	objects = IdentityProviderManager()

	domain = models.CharField(max_length=150, verbose_name=_("domain"), help_text=_("Example: accounts.google.com; may include a path"), unique=True)

	name = models.CharField(max_length=150, blank=True)

	client_id = models.CharField(max_length=150, blank=True)
	client_secret = models.TextField(blank=True)

	protocol = models.CharField(max_length=50, verbose_name=_("protocol"), choices=PROTOCOL_CHOICES, default='openid_connect', blank=True)
	protocol_settings_yaml = models.TextField(blank=True, verbose_name=_("protocol-specific settings"), help_text=_("In YAML. Usually empty."))

	inherit_admin_status = models.BooleanField(default=False, help_text="Grant superuser status to the provider's admins.")

	def __str__(self):
		if self.name:
			return self.name
		else:
			return self.domain

	@property
	def protocol_settings(self):
		if self.protocol_settings_yaml:
			kwargs = yaml.load(self.protocol_settings_yaml)
		else:
			return {}

	@property
	def client(self):
		if self.protocol:
			return connect('https://' + self.domain + ('/' if not '/' in self.domain else ''), self.client_id, self.client_secret, protocol=self.protocol if self.protocol != 'openid_connect' else None, **self.protocol_settings)
		else:
			return None

	def save(self, *args, **kwargs):
		self.client
		super().save(*args, **kwargs)

	def redirect_uri(self, request):
		return request.build_absolute_uri(reverse('extauth:oauth-done'))

class ExternalIdentityManager(models.Manager):

	def forced_get(self, email=None, sub=None, provider=None):
		try:
			if email:
				return self.get(email=email)
			else:
				return self.get(sub=sub, provider=provider)
		except ExternalIdentity.DoesNotExist:
			ei = ExternalIdentity()
			if email:
				ei.email = email
			else:
				ei.sub = sub
				ei.provider = provider
			return ei

	def get(self, email=None, **kwargs):
		if email:
			sub, domain = email.split('@', 1)
			return super().get(sub=sub, provider__domain=domain, **kwargs)
		return super().get(**kwargs)

	def create(self, sub=None, provider=None, email=None, **kwargs):
		if not (sub and provider) and email:
			sub, domain = email.split('@', 1)
			provider, created = IdentityProvider.objects.get_or_create(domain=domain, defaults={'protocol': ''})

		return super().create(sub=sub, provider=provider, **kwargs)

	def get_or_create(self, sub=None, provider=None, email=None, **kwargs):
		if not (sub and provider) and email:
			sub, domain = email.split('@', 1)
			provider, created = IdentityProvider.objects.get_or_create(domain=domain, defaults={'protocol': ''})

		return super().get_or_create(sub=sub, provider=provider, **kwargs)

class Profile:
	def __init__(self, data):
		self.__dict__ = data

	def __getattr__(self, attr):
		return self.__dict__.get(attr, '')

class ExternalIdentity(models.Model):
	objects = ExternalIdentityManager()

	class Meta:
		verbose_name_plural = 'External identities'
		unique_together = (('sub', 'provider'),)

	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	trusted = models.BooleanField(default=False)

	sub = models.CharField(max_length=150)
	provider = models.ForeignKey(IdentityProvider)

	userinfo_yaml = models.TextField(verbose_name="User information", blank=True)

	@property
	def exists(self):
		try:
			return self.user
		except ExternalIdentity.user.RelatedObjectDoesNotExist:
			return None

	@property
	def email(self):
		return self.sub + '@' + self.provider.domain

	@email.setter
	def email(self, email):
		self.sub, domain = email.split('@', 1)
		self.provider, created = IdentityProvider.objects.get_or_create(domain=domain, defaults={'protocol': ''})

	@property
	def external_name(self):
		return self.profile.nickname or self.profile.name or self.sub

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
		return Profile(self.userinfo)

	@property
	def additional_identities(self):
		ais = []

		email = self.userinfo.get('email')
		if email and self.userinfo.get('email_verified'):
			ais.append(ExternalIdentity.objects.forced_get(email=email))

		return ais

def create_user(username):
	User = auth.get_user_model()

	base_username = username[0:130] # Django has 150 char limit, we need shorter for retrying.

	username = base_username
	last_error = None
	for i in range(1, 11): # Try 10 times
		try:
			return User.objects.create(username=username)
		except IntegrityError as e:
			username = base_username + str(random.randrange(0, 10**i))
			last_error = e

	raise last_error
