from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import ExternalIdentity


class UserMixin:

	@property
	def url(self):
		return reverse('extauth:account-home', args=[self.id])

	@property
	def emails(self):
		return [ei.email for ei in self.externalidentity_set.filter(provider__protocol="")]

	@emails.setter
	def emails(self, val):
		for ei in self.external_identities:
			if not ei.email in val:
				ei.delete()

		eis = [ExternalIdentity.objects.forced_get(email=email) for email in val]
		for ei in eis:
			ei.user = self
			ei.trusted = True
			ei.save()

	@property
	def email(self):
		# TODO Provide a way to choose the main email address.
		try:
			return self.emails[0]
		except IndexError:
			return ''

	@property
	def external_identities(self):
		return self.externalidentity_set.all()

	@property
	def trusted_external_identities(self):
		return self.externalidentity_set.filter(trusted=True)

	@property
	def login_with(self):
		login_with = list(self.trusted_external_identities.exclude(provider__protocol=""))
		if self.has_usable_password():
			login_with.append(_("password"))
		return login_with

	@property
	def reset_password_with(self):
		reset_password_with = list(self.trusted_external_identities.filter(provider__protocol=""))
		return reset_password_with
