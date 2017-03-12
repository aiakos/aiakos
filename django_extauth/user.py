from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


def user_external_identities(user):
	return user.externalidentity_set.all()

User.external_identities = property(user_external_identities)


def user_trusted_external_identities(user):
	return user.externalidentity_set.filter(trusted=True)

User.trusted_external_identities = property(user_trusted_external_identities)


def user_login_with(user):
	login_with = list(user.trusted_external_identities.exclude(provider__protocol=""))
	if user.has_usable_password():
		login_with.append(_("password"))
	return login_with

User.login_with = property(user_login_with)


def user_reset_password_with(user):
	reset_password_with = list(user.trusted_external_identities.filter(provider__protocol=""))
	return reset_password_with

User.reset_password_with = property(user_reset_password_with)
