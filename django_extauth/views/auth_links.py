from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.urls import reverse

from six.moves.urllib.parse import urlencode

from ..token import auth_token


def login_link(email):
	token = auth_token(email)
	return settings.BASE_HOST + reverse('extauth:login-by-email', args=[token])

def password_reset_link(site, email, user, **kwargs):
	url = reverse('extauth:account-settings', args=[user.id])
	if kwargs:
		url += '?' + urlencode(kwargs)
	url += "#reset"

	token = auth_token(email)
	return settings.BASE_HOST + reverse('extauth:login-by-email', args=[token]) + '?' + urlencode({
		REDIRECT_FIELD_NAME: url,
	})

def finish_registration_by_email_link(site, email, user, **kwargs):
	token = auth_token(email, user_id = str(user.id))
	url = settings.BASE_HOST + reverse('extauth:finish-registration-by-email', args=[token])
	if kwargs:
		url += '?' + urlencode(kwargs)
	return url
