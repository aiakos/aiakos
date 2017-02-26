import logging
from base64 import b64decode

from django.contrib.auth import authenticate
from django.utils.cache import patch_vary_headers

from .decorators import oauth_error_response
from .errors import *
from .tokens import expandAccessToken

logger = logging.getLogger(__name__)

def get_auth(request, scheme):
	header = request.META.get('HTTP_AUTHORIZATION', '')
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

def BearerTokenAuth(get_response):
	"""
	Middleware for OAuth2 user authentication

	This middleware is able to work along with AuthenticationMiddleware and its behaviour depends
	on the order it's processed with.

	If it comes *after* AuthenticationMiddleware and request.user is valid, leave it as is and does
	not proceed with token validation. If request.user is the Anonymous user proceeds and try to
	authenticate the user using the OAuth2 access token.

	If it comes *before* AuthenticationMiddleware, or AuthenticationMiddleware is not used at all,
	tries to authenticate user with the OAuth2 access token and set request.user field. Setting
	also request._cached_user field makes AuthenticationMiddleware use that instead of the one from
	the session.

	It also adds 'Authorization' to the 'Vary' header. So that django's cache middleware or a
	reverse proxy can create proper cache keys
	"""
	@oauth_error_response(logger)
	def middleware(request):
		token = get_auth(request, 'Bearer')
		if token is not None:
			try:
				request.token = expandAccessToken(token)
			except ValueError:
				raise invalid_token()

			if not hasattr(request, 'user') or request.user.is_anonymous:
				request.user = request._cached_user = token.user

		response = get_response(request)
		patch_vary_headers(response, ('Authorization',))
		return response

	return middleware

def ClientSecretBasicAuth(get_response):
	@oauth_error_response(logger)
	def middleware(request):
		credentials = get_auth(request, 'Basic')
		if credentials is not None:
			uname, passwd = b64decode(credentials.encode('ascii')).decode('utf-8').split(':')
			user = authenticate(request=request, user_id=uname, password=passwd)
			if not user:
				raise invalid_client()

			if not hasattr(request, 'user') or request.user.is_anonymous:
				request.user = request._cached_user = user

		response = get_response(request)
		patch_vary_headers(response, ('Authorization',))
		return response

	return middleware
