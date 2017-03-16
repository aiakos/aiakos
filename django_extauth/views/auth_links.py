from django.contrib.auth import REDIRECT_FIELD_NAME
from django.urls import reverse

from six.moves.urllib.parse import urlencode

from ..token import auth_token


def password_reset_link(site, email):
	token = auth_token(email)
	return 'https://' + site.domain + reverse('extauth:login-by-email', args=[token]) + '?' + urlencode({
		REDIRECT_FIELD_NAME: reverse('change-password')
	})

def finish_registration_by_email_link(site, email, user):
	token = auth_token(email, user_id = user.id)
	return 'https://' + site.domain + reverse('extauth:finish-registration-by-email', args=[token])