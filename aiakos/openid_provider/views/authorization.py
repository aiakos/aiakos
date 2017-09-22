import json
import logging
from uuid import uuid4

from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from ..errors import *
from .auth_request import AuthRequest, BadRequest, badrequest_handler

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(badrequest_handler, name='dispatch')
class AuthorizationView(View):

	def _handle(self, request, auth_request):
		if not auth_request['redirect_uri']:
			raise BadRequest(_("Missing redirect_uri."))

		try:
			if auth_request['request']:
				raise request_not_supported()

			if auth_request['request_uri']:
				raise request_uri_not_supported()

			prompt = set(auth_request['prompt'].split(' ')) - {''}

			if 'none' in prompt and len(prompt) > 1:
				raise invalid_request()

			for p in prompt:
				if not p in {'none', 'select_account', 'consent'}:
					raise server_error("Unimplemented prompt type.")

			if 'max_age' in auth_request:
				raise server_error("max_age is not implemented.")

			data = json.dumps(auth_request.data)
			id = uuid4().hex

			res = redirect(reverse('openid_provider:select-account') + '?request=' + id)
			request.session.setdefault('auth_requests', {})[id] = data
			request.session.modified = True
			return res

		except OAuthError as e:
			logger.debug("OAuth error", exc_info=True)
			return auth_request.deny(e)

	def get(self, request):
		return self._handle(request, AuthRequest(request, request.GET))

	def post(self, request):
		return self._handle(request, AuthRequest(request, request.POST))
