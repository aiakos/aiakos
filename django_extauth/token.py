import logging
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from jose import JOSEError, jwt

from .models import ExternalIdentity

User = get_user_model()

def auth_token(sub=None, **data):
	return jwt.encode(dict(
		sub = sub,
		exp = int((timezone.now() + timedelta(days=3)).timestamp()),
		**data
	), settings.SECRET_KEY, algorithm='HS256')

def authenticate_token(request, token):
	request.token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

	sub = request.token['sub']
	if '@' in sub:
		request.external_identity = ExternalIdentity.objects.forced_get(email=sub)
		if request.external_identity.exists:
			auth_login(request, request.external_identity.user)
			messages.info(request, _("You've signed in."))
	else:
		request.user = User.objects.get(id=sub)

def in_url_authentication(func):
	def wrapper(request, auth_token, **kwargs):
		authenticate_token(request, auth_token)
		return func(request, **kwargs)
	return wrapper
