from django.utils.translation import gettext_lazy as _


class UserMixin:

	@property
	def email(self):
		# TODO Provide a way to choose the main email address.
		try:
			return self.externalidentity_set.filter(provider__protocol="")[0].email
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
