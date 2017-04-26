import json
import logging
from base64 import b64encode
from datetime import datetime
from urllib.parse import urlencode, urlsplit, urlunsplit
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _

from ..models import Client


class BadRequest(Exception):
	pass


class NotFound(Exception):
	pass


def _load_data(request):
	try:
		id = request.POST['request']
	except:
		try:
			id = request.GET['request']
		except:
			return

	try:
		return id, json.loads(request.COOKIES['auth_request_' + id])
	except Exception as e:
		logger.warning(e)


RESPONSE_MODES = {
	'fragment',
	'query',
	'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
}

class AuthRequest:
	def __init__(self, request, data = None):
		self.http_request = request

		self.id, self.data = _load_data(request) or (None, data)

		if not self.data:
			raise BadRequest()

		self.response_type = set(self['response_type'].split(' ')) - {''}
		self.response_mode = self.get('response_mode', 'fragment' if self.response_type != {'code'} else 'query')

		if self.response_mode not in RESPONSE_MODES:
			raise BadRequest(_("Invalid response_mode."))

		if self.response_mode == 'query' and (self.response_type - {'code'}):
			raise BadRequest(_("Query can be used only with response_type=code."))

		self.state = self['state']

		self.nonce = self['nonce']
		if self.nonce == '' and (self.response_type - {'code'}):
			raise BadRequest(_("Missing nonce."))

		User = get_user_model()
		client_id = self['client_id']
		if not self['client_id']:
			raise BadRequest(_("Missing client_id."))
		try:
			service_account = User.objects.get(id=self['client_id'])
		except (User.DoesNotExist, ValueError):
			try:
				service_account = User.objects.get(username=self['client_id'])
			except (User.DoesNotExist, ValueError):
				raise NotFound(_("Invalid client_id."))

		try:
			self.client = service_account.openid_client
		except Client.DoesNotExist:
			raise NotFound(_("Invalid client_id."))

		self.redirect_uri = self['redirect_uri']
		if not self.redirect_uri:
			raise BadRequest(_("Missing redirect_uri."))

		if self.redirect_uri not in self.client.redirect_uris:
			raise NotFound(_("Invalid redirect_uri."))

	def __getitem__(self, key):
		return self.data.get(key, '')

	def get(self, key, default=None):
		return self.data.get(key, default)

	def __contains__(self, key):
		return self[key] != ''

	def respond(self, response):
		if self.response_mode in {'query', 'fragment'}:
			if self.state:
				response['state'] = self.state

			redirect_uri = urlsplit(self.redirect_uri)

			if self.response_mode == 'query':
				new_query = redirect_uri.query
				if new_query:
					new_query += '&'
				new_query += urlencode(response)
				redirect_uri = redirect_uri._replace(query=new_query)

			elif self.response_mode == 'fragment':
				new_fragment = redirect_uri.fragment
				if new_fragment:
					new_fragment += '&'
				new_fragment += urlencode(response)
				redirect_uri = redirect_uri._replace(fragment=new_fragment)

			return redirect(urlunsplit(redirect_uri))

		if self.response_mode == 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST':
			saml_response = SAMLResponse(response['saml'])
			print(saml_response)
			return render(self.http_request, 'openid_provider/saml_submit.html', {
				'redirect_uri': self.redirect_uri,
				'RelayState': self.state,
				'SAMLResponse': b64encode(saml_response.encode('utf-8')) if 'saml' in response else '',
			})

	def deny(self, e):
		return self.respond({
			'error': type(e).__name__,
			'error_description': e.description,
		})

SAML_RESPONSE = '<Response xmlns="urn:oasis:names:tc:SAML:2.0:protocol" Version="2.0" ID="_{}" IssueInstant="{}">{}</Response>'

SAML_STATUS_OK = '<Status><StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/></Status>'

def SAMLResponse(data):
	return SAML_RESPONSE.format(uuid4().hex, datetime.utcnow().isoformat() + "Z", SAML_STATUS_OK + data)
