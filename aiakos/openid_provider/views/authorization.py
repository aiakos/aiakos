import logging

from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from aiakos.flow import Flow

from ..errors import *
from ..flows import authorize
from .oauth_request import AuthorizationRequest, BadRequest, badrequest_handler


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(badrequest_handler, name='dispatch')
class AuthorizationView(View):

	def _handle(self, request, data):
		auth_request = AuthorizationRequest.parse(data)

		if not auth_request.client_id:
			raise BadRequest(_("Missing client_id."))

		if not auth_request.redirect_uri:
			raise BadRequest(_("Missing redirect_uri."))

		if auth_request.prompt - {'none', 'select_account', 'consent'}:
			raise BadRequest(_("Unsupported prompt type."))

		request.flow = Flow()
		request.flow.auth_request = auth_request

		return authorize(request)

	def get(self, request):
		return self._handle(request, request.GET)

	def post(self, request):
		return self._handle(request, request.POST)
