import json
import logging
from base64 import b64encode
from datetime import datetime
from urllib.parse import urlencode, urlsplit, urlunsplit
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _

from jose import jwt

log = logging.getLogger(__name__)


class BadRequest(Exception):
	pass

def badrequest_handler(get_response):
	def handler(request, *args, **kwargs):
		try:
			return get_response(request, *args, **kwargs)
		except BadRequest as e:
			return HttpResponseBadRequest(e.args[0])
	return handler


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
		log.warning(e)


RESPONSE_MODES = {
	'fragment',
	'query',
}

User = get_user_model()

class AuthRequest:
	redirect_uri_set = 'redirect_uris'

	def __init__(self, request, data = None):
		self.http_request = request

		self.id, self.data = _load_data(request) or (None, data)

		if not self.data:
			raise BadRequest()

		self.response_type = set(self['response_type'].split(' ')) - {''}
		self.response_mode = self['response_mode'] or ('fragment' if self.response_type != {'code'} else 'query')

		if self.response_mode not in RESPONSE_MODES:
			raise BadRequest(_("Invalid response_mode."))

		if self.response_mode == 'query' and (self.response_type - {'code'}):
			raise BadRequest(_("Query can be used only with response_type=code."))

		self.state = self['state']

		self.nonce = self['nonce']
		if self.nonce == '' and (self.response_type - {'code'}):
			raise BadRequest(_("Missing nonce."))

		self.id_token_hint = self['id_token_hint']
		if self.id_token_hint:
			## TODO Verify the JWT securely
			# Note: this is hard because it might have expired already, and we're going to rotate signing keys
			# OTOH we're probably going to keep them for 24h after we've stopped signing with them, and older id_tokens should not be tolerared
			self.id_hint = jwt.get_unverified_claims(self['id_token_hint'])
			self.id_hint_valid = False
		else:
			self.id_hint = None
			self.id_hint_valid = False

		client_id = self['client_id']

		if self.id_hint:
			if client_id:
				if self.id_hint['aud'] != client_id:
					raise BadRequest(_("Invalid id_token_hint."))
			else:
				client_id = self.id_hint['aud']

		if not client_id:
			raise BadRequest(_("Missing client_id."))
		try:
			self.client = User.objects.get(id=client_id)
		except (User.DoesNotExist, ValidationError):
			raise BadRequest(_("Invalid client_id."))

		if not self.client.oauth_app:
			raise BadRequest(_("Invalid client_id."))

		self.redirect_uri = self['redirect_uri']

		if self.redirect_uri and (not self.redirect_uri_set or self.redirect_uri not in getattr(self.client, 'oauth_' + self.redirect_uri_set)):
			raise BadRequest(_("Invalid redirect_uri."))

	@property
	def redirect_host(self):
		return urlsplit(self.redirect_uri).hostname

	def __getitem__(self, key):
		if hasattr(self, key):
			return getattr(self, key)

		return self.data.get(key) or ''

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

	def deny(self, e):
		return self.respond({
			'error': type(e).__name__,
			'error_description': e.description,
		})
