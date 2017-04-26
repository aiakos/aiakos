import json
import logging
from base64 import b64decode
from urllib.parse import urlencode, urlsplit, urlunsplit
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt, csrf_protect, requires_csrf_token
from django.views.generic import View

from defusedxml.ElementTree import fromstring as parse_xml

from ...errors import *
from ...models import Client, UserConsent
from ...scopes import SCOPES
from ...tokens import *
from ...views import AuthorizationView
from ...views.auth_request import AuthRequest, BadRequest, NotFound
from .deflate import inflate

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class SAMLAuthorizationView(AuthorizationView):

	def _handle_saml(self, request, saml_request, state):
		if saml_request.tag != '{urn:oasis:names:tc:SAML:2.0:protocol}AuthnRequest':
			raise BadRequest("Invalid SAMLRequest")

		issuers = list(saml_request.iter('{urn:oasis:names:tc:SAML:2.0:assertion}Issuer'))
		if len(issuers) != 1:
			raise BadRequest("Invalid SAMLRequest")
		issuer = issuers[0].text

		id = saml_request.attrib.get('ID', '')
		consumer_url = saml_request.attrib.get('AssertionConsumerServiceURL', '')
		consumer_proto = saml_request.attrib.get('ProtocolBinding', '')

		consumer_index = saml_request.attrib.get('AssertionConsumerServiceIndex', '')

		if not "://" in issuer:
			issuer = "https://" + issuer

		auth_request = AuthRequest(request, dict(
			client_id = issuer,
			redirect_uri = consumer_url,
			response_mode = consumer_proto,
			state = state,
			response_type = 'saml',
			scope = 'openid',
			nonce = id,
		))

		return self._handle(request, auth_request)

	def get(self, request):
		state = request.GET.get('RelayState', '')

		try:
			saml_request_xml = inflate(b64decode(request.GET['SAMLRequest'])).decode('utf-8')
			saml_request = parse_xml(saml_request_xml, forbid_dtd=True)
		except:
			raise BadRequest("Invalid SAMLRequest")

		print(state, saml_request_xml)

		return self._handle_saml(request, saml_request, state)

	def post(self, request):
		state = request.POST.get('RelayState', '')

		try:
			saml_request_xml = b64decode(request.POST['SAMLRequest']).decode('utf-8')
			saml_request = parse_xml(saml_request_xml, forbid_dtd=True)
		except:
			raise BadRequest("Invalid SAMLRequest")

		print(state, saml_request_xml)

		return self._handle_saml(request, saml_request, state)
