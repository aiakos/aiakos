from django.http import HttpResponseBadRequest
from django.utils.translation import ugettext_lazy as _

from .. import jwt
from ..auth_request import AuthRequest


class BadRequest(Exception):
	pass


def badrequest_handler(get_response):
	def handler(request, *args, **kwargs):
		try:
			return get_response(request, *args, **kwargs)
		except BadRequest as e:
			return HttpResponseBadRequest(e.args[0])
	return handler


RESPONSE_MODES = {
	'fragment',
	'query',
}

QUERY_ALLOWED = {
	frozenset(),
	frozenset({'none'}),
	frozenset({'code'}),
}

QUERY_DEFAULT = QUERY_ALLOWED


class InputDict:  # We're treating all missing params as params with no value
	def __init__(self, data):
		self._data = data

	def __getitem__(self, name):
		return self._data.get(name, '')

	def __getattr__(self, name):
		return self[name]


class OAuthRequest:
	redirect_uri_param = None

	@classmethod
	def parse(kind, data):
		oauth_req = InputDict(data)

		self = AuthRequest()

		self.response_type = frozenset(oauth_req.response_type.split(' ')) - {''}
		if 'none' in self.response_type and len(self.response_type) > 1:
			raise BadRequest(_("Invalid response_type."))

		self.response_mode = oauth_req.response_mode or ('query' if self.response_type in QUERY_DEFAULT else 'fragment')

		if self.response_mode not in RESPONSE_MODES:
			raise BadRequest(_("Invalid response_mode."))

		if self.response_mode == 'query' and self.response_type not in QUERY_ALLOWED:
			raise BadRequest(_("Query response_mode is not allowed for given response_type."))

		self.state = oauth_req.state

		self.nonce = oauth_req.nonce
		if self.nonce == '' and (self.response_type - {'code', 'none'}):
			raise BadRequest(_("Missing nonce."))

		self.prompt = frozenset(oauth_req.prompt.split(' ')) - {''}
		if 'none' in self.prompt and len(self.prompt) > 1:
			raise BadRequest(_("Invalid prompt."))

		self.scope = frozenset(oauth_req.scope.split(' ')) - {''}

		self.id_hint = None
		self.id_hint_valid = False

		self.id_token_hint = oauth_req.id_token_hint
		if self.id_token_hint:
			# Note: we're not checking aud here, as aud is the client id.
			try:
				self.id_hint = jwt.decode(None, [jwt.myself], self.id_token_hint)
				self.id_hint_valid = True
			except jwt.JWTError as e:
				if hasattr(e, 'payload'):
					self.id_hint = e.payload

		self.client_id = oauth_req.client_id
		if self.id_hint:
			aud = self.id_hint['aud']
			if isinstance(aud, list):
				if len(aud) > 1:
					raise BadRequest(_("Invalid id_token_hint."))
				aud = aud[0]

			if self.client_id:
				if aud != self.client_id:
					raise BadRequest(_("Invalid id_token_hint."))
			else:
				self.client_id = aud

		if self.client_id:
			if not self.client:
				raise BadRequest(_("Invalid client_id."))

			if kind.redirect_uri_param:
				self.redirect_uri = oauth_req[kind.redirect_uri_param]

				if self.redirect_uri and self.redirect_uri not in getattr(self.client, 'oauth_' + kind.redirect_uri_set):
					raise BadRequest(kind.redirect_uri_invalid)

		return self


class AuthorizationRequest(OAuthRequest):
	redirect_uri_param = 'redirect_uri'
	redirect_uri_set = 'redirect_uris'
	redirect_uri_invalid = _("Invalid redirect_uri.")


class EndSessionRequest(OAuthRequest):
	redirect_uri_param = 'post_logout_redirect_uri'
	redirect_uri_set = 'post_logout_redirect_uris'
	redirect_uri_invalid = _("Invalid post_logout_redirect_uri.")
