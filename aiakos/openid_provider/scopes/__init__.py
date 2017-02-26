from django.conf import settings

if hasattr(settings, 'SCOPES'):
	SCOPES = settings.SCOPES

elif 'django_profile_oidc' in settings.INSTALLED_APPS:
	from .profile_oidc import ProfileScope
	from .email_oidc import EmailScope
	from .phone_oidc import PhoneScope
	from .address_oidc import AddressScope

	SCOPES = {
		'profile': ProfileScope,
		'email': EmailScope,
		'phone': PhoneScope,
		'address': AddressScope,
	}

else:
	from .profile_django import ProfileScope
	from .email_django import EmailScope

	SCOPES = {
		'profile': ProfileScope,
		'email': EmailScope,
	}

if hasattr(settings, 'CUSTOM_SCOPES'):
	SCOPES.update(settings.CUSTOM_SCOPES)
