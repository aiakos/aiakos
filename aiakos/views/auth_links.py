from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from ..tokens import makeEmailConfirmationToken


def password_reset_link(user, site):
	return 'https://' + site.domain + reverse('password_reset_confirm', kwargs={
		'uidb64': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
		'token': default_token_generator.make_token(user),
	})

def email_confirmation_link(user, email, site):
	token = makeEmailConfirmationToken(user, email)
	return 'https://' + site.domain + reverse('confirm_email', args=[token])
