from django.conf import settings
from django.contrib.auth import get_user_model

if hasattr(settings, 'SCOPES'):
	SCOPES = settings.SCOPES

else:
	from .profile import ProfileScope
	from .email import EmailScope
	from .phone import PhoneScope
	from .address import AddressScope

	User = get_user_model()

	SCOPES = {
		'profile': ProfileScope,
	}

	if hasattr(User, 'email'):
		SCOPES['email'] = EmailScope

	if hasattr(User, 'phone_number'):
		SCOPES['phone'] = PhoneScope

	if hasattr(User, 'address'):
		SCOPES['address'] = AddressScope

if hasattr(settings, 'CUSTOM_SCOPES'):
	SCOPES.update(settings.CUSTOM_SCOPES)
