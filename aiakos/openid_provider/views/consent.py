from datetime import datetime, timedelta
from uuid import uuid4

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView

from ..errors import consent_required
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
		context['hidden_inputs'] = mark_safe('<input type="hidden" name="request" value="{}">'.format(self.auth_request.id)),

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

		saml = None
		if 'saml' in self.auth_request.response_type and 'openid' in scope:
			saml = makeSAMLAssertion(request=self.request, auth_request=self.auth_request, user=self.request.user, scope=scope, nonce=self.auth_request.nonce, at=access_token, c=code)
			response['saml'] = saml

		id_token = None
		if 'id_token' in self.auth_request.response_type and 'openid' in scope:
			id_token = makeIDToken(request=self.request, client=self.auth_request.client, user=self.request.user, scope=scope, nonce=self.auth_request.nonce, at=access_token, c=code)
			response['id_token'] = id_token

		return self.auth_request.respond(response)

def makeSAMLAssertion(request, auth_request, user, scope, nonce, at, c):
	return """
		<Assertion xmlns="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xs="http://www.w3.org/2001/XMLSchema" ID="{ID}" Version="2.0" IssueInstant="{iat}">
			<Issuer>http://localhost.aiakosauth.io/saml2/authorize</Issuer>
			<Subject>
				<NameID SPNameQualifier="https://sp.testshib.org/shibboleth-sp" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient">_ce3d2948b4cf20146dee0a0b3dd6f69b6cf86f62d7</NameID>
				<SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
					<SubjectConfirmationData NotBefore="{nbf}" NotOnOrAfter="{exp}" Recipient="{redirect_uri}" InResponseTo="{nonce}"/>
				</SubjectConfirmation>
			</Subject>
			<Conditions NotBefore="{nbf}" NotOnOrAfter="{exp}">
				<AudienceRestriction>
					<Audience>https://sp.testshib.org/shibboleth-sp</Audience>
				</AudienceRestriction>
			</Conditions>
		</Assertion>
		""".format(
			ID = uuid4().hex,
			iat = datetime.utcnow().isoformat() + 'Z',
			nbf = (datetime.utcnow() - timedelta(minutes=10)).isoformat() + 'Z',
			exp = (datetime.utcnow() + timedelta(hours=12)).isoformat() + 'Z',
			nonce = nonce,
			redirect_uri = auth_request.redirect_uri,
		)
