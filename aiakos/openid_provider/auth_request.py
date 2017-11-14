from urllib.parse import urlencode, urlsplit, urlunsplit

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import redirect

from cached_property import cached_property

from ..serializable import Container, Set

Account = get_user_model()


class AuthRequest(Container):

	class Fields:
		response_type = Set
		response_mode = None
		state = None
		nonce = None
		prompt = Set
		scope = Set
		id_hint = None
		id_hint_valid = None
		id_token_hint = None
		client_id = None
		redirect_uri = None

	@cached_property
	def client(self):
		try:
			return Account.objects.exclude(oauth_app=None).get(id=self.client_id)
		except (Account.DoesNotExist, ValidationError):
			return None

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
		# We're not going to be an open redirector.
		raise e

		# TODO Render a page with error description and, if there is a redirect_uri, a button to fire the following:
		return self.respond({
			'error': type(e).__name__,
			'error_description': e.description,
		})
