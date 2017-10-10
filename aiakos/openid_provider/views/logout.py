import logging

from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .auth_request import AuthRequest, badrequest_handler


class LogoutRequest(AuthRequest):
	redirect_uri_set = 'post_logout_redirect_uris'


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(badrequest_handler, name='dispatch')
class LogoutView(View):

	def get(self, request):
		client_id = request.GET.get('client_id')  # See https://bitbucket.org/openid/connect/issues/914/session-5-missing-client_id-parameter
		id_token_hint = request.GET.get('id_token_hint')
		post_logout_redirect_uri = request.GET.get('post_logout_redirect_uri')

		if id_token_hint or post_logout_redirect_uri:
			req = LogoutRequest(request, dict(
				response_type = '',
				response_mode = 'query',
				client_id = client_id,
				id_token_hint = id_token_hint,
				redirect_uri = post_logout_redirect_uri,
				state = request.GET.get('state'),
			))
		else:
			req = None

		if request.user.is_authenticated:
			if not req or not req.id_hint_valid or req.id_hint['sub'] not in (str(acc.id) for acc in request.user.accounts):
				if not getattr(settings, 'INSECURE_END_SESSION_ENDPOINT', False):
					raise NotImplementedError('Logout confirmation view is not yet implemented')

			logout(request)

		if not req or not req.redirect_uri:
			return redirect(settings.LOGOUT_REDIRECT_URL)

		return req.respond({})
