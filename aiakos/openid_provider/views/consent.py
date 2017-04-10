from datetime import datetime, timedelta
from uuid import uuid4

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView

from defusedxml.lxml import fromstring as parse_xml
from lxml import etree
from signxml import XMLSigner

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
	return etree.tostring(signer.sign(parse_xml("""
		<Assertion xmlns="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" ID="{ID}" Version="2.0" IssueInstant="{iat}">

			<Issuer>http://localhost.aiakosauth.io:8000/saml2/authorize/</Issuer>

			<ds:Signature Id="placeholder"></ds:Signature>

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

			<AuthnStatement AuthnInstant="{auth_time}">
				<AuthnContext>
					<AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified</AuthnContextClassRef>
				</AuthnContext>
			</AuthnStatement>

		</Assertion>
		""".format(
			ID = uuid4().hex,
			iat = datetime.utcnow().isoformat() + 'Z',
			nbf = (datetime.utcnow() - timedelta(minutes=10)).isoformat() + 'Z',
			exp = (datetime.utcnow() + timedelta(hours=12)).isoformat() + 'Z',
			nonce = nonce,
			redirect_uri = auth_request.redirect_uri,

			auth_time = (datetime.utcnow() - timedelta(hours=24)).isoformat() + 'Z', # TODO
		)), key=KEY, cert=CERT)).decode('utf-8')

signer = XMLSigner(c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#")

# Don't worry, it's not used anywhere else.
# TODO use key from the database
KEY = b"""-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCbBiBek4L/xUOFEvXhPTYf8ddEdx8/ZDTEmLj2/csTjCmwdQ1c
fnT45gRwFapCcO2fz7nvyKJFKOt+HHCtHt0UOuI7tvCwN5lmPCIBHMiaLCy1s/oO
RQY2L6Yez1I1BRjyXPeme6RFiJ/QYr8pzmt3Ut8VHSGrH08nucG1JY1uPQIDAQAB
AoGACB8DypiVNAN4REwoO966S2Wetpw785TzC7qJdAz7GsDMvU0AgHAyfgiEwn9s
DjN+y1C1R6m90HwyjAZ+457ai3wS9UsTQPfgr2iGTH64tR9BgqCconBGHzb34+/a
7JimGyCOqiyz6xFqOZ7xTaWtxm9T0terliX4mASFahfRZEkCQQC3/dG9wfCjQkO9
dOcyAA1LMOs6+z81FdVLF8IiKJhTxcE+9wPgfhGIxn7TwihlL3alppRfOmpoFSR0
mHVUueiJAkEA17IJXz1lqbqjkdex6otrMmYJNbyluQw178n3EDt+HZjHEt7bzqXk
3HbyNv0cVJEqezSmb1E0VWqqzxe3z4XDFQJAR7GWxetJWkRa4vsnj3snsvHn5z65
nXTZfP5P/kF1QcdgCqn0D8jwCizWhKs2VF9PSzMCw6yeg9ohL3Gs3ovmiQJBAJts
dsRiAXekPWlB+7n+bGgMjmZiYShOXC9FYPoZZG7/P7OhUtI9SAR00WQ+TsPBNtNA
xQ1BfmxuSFahyJmI0WECQC8v7qzjU4Iqn0nHYKYD/Dm1PGLtB+kNlGKLngoIJjZJ
5C3/EFYxcF9cXaoe6k5UUryVUVwCVhpzeWE194UQ5aQ=
-----END RSA PRIVATE KEY-----"""

CERT = b"""
-----BEGIN CERTIFICATE-----
MIICWDCCAcGgAwIBAgIJALYjtCnWK2D0MA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
BAYTAlBMMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMTcwNDEwMjAyMDA5WhcNMTgwNDEwMjAyMDA5WjBF
MQswCQYDVQQGEwJQTDETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKB
gQCbBiBek4L/xUOFEvXhPTYf8ddEdx8/ZDTEmLj2/csTjCmwdQ1cfnT45gRwFapC
cO2fz7nvyKJFKOt+HHCtHt0UOuI7tvCwN5lmPCIBHMiaLCy1s/oORQY2L6Yez1I1
BRjyXPeme6RFiJ/QYr8pzmt3Ut8VHSGrH08nucG1JY1uPQIDAQABo1AwTjAdBgNV
HQ4EFgQUnhBKpddmI0yT+rjpmRzrRo6783wwHwYDVR0jBBgwFoAUnhBKpddmI0yT
+rjpmRzrRo6783wwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOBgQAL7R0m
M3CCGvCPu4HAYIkvA/z4TD5ik/B9VFeQluRFxjBmuaeAibGr9a5fN90NbDkj0CUD
OLmYrkQFwgA0PLe44XcPJvtxAjD1WErgrKUNw2aj/XeGc+DouVlTTOcplHTrs+Ej
2xFmvkK4XeMdX5oDvRKQcoL/OdGlOReDc1MFXw==
-----END CERTIFICATE-----
"""
