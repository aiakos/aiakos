from datetime import datetime, timedelta, timezone
from uuid import uuid4

from django.contrib.auth.decorators import login_required
from django.template import Context, Template
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView

from ..errors import access_denied, consent_required
from ..models import UserConsent
from ..scopes import SCOPES
from ..tokens import *
from .auth_request import AuthRequest


@method_decorator(login_required, name='dispatch')
class ConsentView(TemplateView):
	template_name = 'openid_provider/authorize.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['client'] = self.auth_request.client
		context['scope'] = {name: desc for name, desc in SCOPES.items() if name in self.req_untrusted_scope}
		context['hidden_inputs'] = mark_safe('<input type="hidden" name="request" value="{}">'.format(self.auth_request.id))
		return context

	def dispatch(self, request):
		self.auth_request = AuthRequest(request)

		self.req_scope = set(self.auth_request['scope'].split(' '))
		self.req_scope &= set(['openid']) | set(SCOPES.keys())

		self.req_untrusted_scope = self.req_scope - self.auth_request.client.trusted_scopes

		self.prompt = self.auth_request['prompt']

		return super().dispatch(request)

	def get(self, request):
		uc = None

		try:
			if self.prompt == 'consent':
				raise consent_required()

			if self.req_untrusted_scope:
				try:
					uc = UserConsent.objects.get(user=self.request.user, client=self.auth_request.client)
					if not self.req_untrusted_scope.issubset(uc.scope):
						raise consent_required()
				except UserConsent.DoesNotExist:
					raise consent_required()

		except consent_required:
			if self.prompt == 'none':
				return self.auth_request.deny(interaction_required())

			return super().get(request)

		return self.go(uc)

	def post(self, request):
		if '_allow' not in request.POST:
			return self.auth_request.deny(access_denied())

		if self.auth_request.client.confidential:
			uc, created = UserConsent.objects.get_or_create(user=request.user, client=self.auth_request.client)
		else:
			uc = UserConsent(user=request.user, client=self.auth_request.client)

		# TODO add a way to turn on and off single permissions
		uc.scope |= self.req_untrusted_scope

		if self.auth_request.client.confidential:
			uc.save()

		return self.go(uc)

	def go(self, uc=None):
		scope = self.auth_request.client.trusted_scopes
		if uc:
			scope |= uc.scope
		scope &= self.req_scope

		response = {}

		code = None
		if 'code' in self.auth_request.response_type:
			code = makeCode(client=self.auth_request.client, user=self.request.user, scope=scope, nonce=self.auth_request.nonce)
			response['code'] = code

		token_type, access_token, expires_in = None, None, None
		if 'token' in self.auth_request.response_type:
			token_type, access_token, expires_in = makeAccessToken(client=self.auth_request.client, user=self.request.user, scope=scope, confidential=False)
			response['token_type'] = token_type
			response['access_token'] = access_token
			response['expires_in'] = expires_in

		id_token = None
		if 'id_token' in self.auth_request.response_type and 'openid' in scope:
			id_token = makeIDToken(request=self.request, client=self.auth_request.client, user=self.request.user, scope=scope, nonce=self.auth_request.nonce, at=access_token, c=code)
			response['id_token'] = id_token

		return self.auth_request.respond(response)
