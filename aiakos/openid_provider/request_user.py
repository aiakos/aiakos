from base64 import b64decode

from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _

from .tokens import expandAccessToken


def get_auth(request, scheme):
	header = request.headers.authorization
	if not header:
		return None

	try:
		given_scheme, given_param = header.split(' ', 1)
	except:
		given_scheme, given_param = header, ''

	if given_scheme.lower() == scheme.lower():
		return given_param
	else:
		return None


def BearerTokenAuth(request):
	params = dict(
		realm = settings.BASE_URL,
	)
	request.auth_challenges.append(('Bearer', params))

	token = get_auth(request, 'Bearer')
	if token is not None:
		try:
			request.token = expandAccessToken(token)
			return request.token.user
		except ValueError:
			params['error'] = 'invalid_token'
			params['error_description'] = _("The access token provided is expired, revoked, malformed, or invalid for other reasons.")


def ClientSecretBasicAuth(request):
	params = dict(
		realm = settings.BASE_URL,
	)
	request.auth_challenges.append(('Basic', params))

	credentials = get_auth(request, 'Basic')
	if credentials is not None:
		uname, passwd = b64decode(credentials.encode('ascii')).decode('utf-8').split(':')
		user = authenticate(request=request, user_id=uname, password=passwd)
		if user:
			return user


def ClientSecretPostAuth(request):
	client_id = request.POST.get('client_id')
	client_secret = request.POST.get('client_secret')

	if client_id and client_secret:
		user = authenticate(request=request, user_id=client_id, password=client_secret)
		if user:
			return user
