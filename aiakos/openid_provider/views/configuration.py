from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import View

from ..issuer import issuer
from ..scopes import SCOPES


class ConfigurationView(View):

	def dispatch(self, request):
		response = super().dispatch(request)
		response['Access-Control-Allow-Origin'] = '*'
		return response

	def get(self, request):
		config = dict(
			issuer = issuer.url,

			authorization_endpoint = request.build_absolute_uri(reverse('openid_provider:authorization')),
			token_endpoint         = request.build_absolute_uri(reverse('openid_provider:token')),
			userinfo_endpoint      = request.build_absolute_uri(reverse('openid_provider:userinfo')),
			jwks_uri               = request.build_absolute_uri(reverse('openid_provider:jwks')),

			response_types_supported = ['code', 'token', 'id_token', 'code token', 'code id_token', 'token id_token', 'code token id_token', 'none'],
			subject_types_supported = ['public'],
			id_token_signing_alg_values_supported = ['RS256'],
			scopes_supported = ['openid'] + list(SCOPES.keys()),
			token_endpoint_auth_methods_supported = ['client_secret_basic', 'client_secret_post'],
		)

		return JsonResponse(config, json_dumps_params={'indent': True})
