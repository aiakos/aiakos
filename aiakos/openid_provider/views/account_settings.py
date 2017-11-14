import logging

from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .oauth_request import OAuthRequest, badrequest_handler


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(badrequest_handler, name='dispatch')
class AccountSettingsView(View):

	def get(self, request):
		id_token_hint = request.GET.get('id_token_hint')

		if id_token_hint:
			req = OAuthRequest.parse(dict(
				response_type = '',
				response_mode = 'query',
				id_token_hint = id_token_hint,
			))

			for acc in request.user.accounts:
				if req.id_hint['sub'] == str(acc.pk):
					return redirect('extauth:settings', user_id=str(acc.pk))

		if request.user.is_authenticated:
			return redirect('extauth:settings', user_id=str(request.user.pk))

		return redirect(settings.LOGIN_REDIRECT_URL)
