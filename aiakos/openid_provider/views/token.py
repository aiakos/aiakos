import logging

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from ..decorators import oauth_error_response
from ..errors import *
from ..tokens import *

logger = logging.getLogger(__name__)

def _auth_code(request):
	try:
		code = request.POST['code']
		redirect_uri = request.POST['redirect_uri']
	except KeyError:
		raise invalid_request()

	try:
		code = expandCode(code)
	except ValueError:
		raise invalid_grant()

	if redirect_uri not in code.client.oauth_redirect_uris:
		raise invalid_grant()

	return code

def _auth_refresh_token(request):
	try:
		rt = request.POST['refresh_token']
	except KeyError:
		raise invalid_request()

	try:
		rt = expandRefeshToken(rt)
	except ValueError:
		raise invalid_grant()

	return rt


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(oauth_error_response(logger), name='dispatch')
class TokenView(View):
	def post(self, request):
		try:
			grant_type = request.POST['grant_type']
		except KeyError:
			raise invalid_request()

		if grant_type == 'authorization_code':
			code = _auth_code(request)
		elif grant_type == 'refresh_token':
			code = _auth_refresh_token(request)
			code.nonce = ''
		else:
			raise unsupported_grant_type()

		if code.client.oauth_auth_method != 'none':
			if request.user != code.client:
				raise invalid_grant()

		# TODO check consent (so we won't generate new tokens after revocation)
		# raise invalid_grant()

		response = {}

		token_type, access_token, expires_in = makeAccessToken(client=code.client, user=code.user, scope=code.scope, confidential=code.client.oauth_auth_method != 'none')
		response['token_type'] = token_type
		response['access_token'] = access_token
		response['expires_in'] = expires_in

		if 'openid' in code.scope:
			id_token = makeIDToken(request, client=code.client, user=code.user, scope=code.scope, nonce=code.nonce, at=access_token)
			response['id_token'] = id_token
		else:
			id_token = None

		if 'offline_access' in code.scope and code.client.oauth_auth_method != 'none':
			refresh_token = makeRefreshToken(client=code.client, user=code.user, scope=code.scope)
			response['refresh_token'] = refresh_token

		response = JsonResponse(response)
		response['Cache-Control'] = 'no-store'
		response['Pragma'] = 'no-cache'
		return response
