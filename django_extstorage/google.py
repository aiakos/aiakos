from base64 import b64encode
from datetime import datetime, timedelta

try:
	from urllib.parse import urlparse, urlencode
except ImportError:
	from urlparse import urlparse, urlencode

import google.auth
from google.auth.transport.requests import AuthorizedSession
from google.auth.transport.requests import Request
from google.auth.iam import Signer

from .http import HTTPStorage

class GoogleStorage(HTTPStorage):
	def __init__(self, base_url=None):
		self.credentials, project = google.auth.default(
			scopes=[
				'https://www.googleapis.com/auth/devstorage.read_only',
				'https://www.googleapis.com/auth/devstorage.read_write',
			]
		)
		self._session = AuthorizedSession(self.credentials)

		super(GoogleStorage, self).__init__(base_url)

	@property
	def _canonical_prefix(self):
		url = urlparse(self.base_url)
		if url.hostname == "storage.googleapis.com":
			return url.path
		else:
			return "/" + url.hostname + url.path

	def url(self, name):
		exp = str(int((datetime.utcnow() + timedelta(hours=1)).timestamp()))

		string_to_sign = "GET\n\n\n{exp}\n{res}".format(
			exp = exp,
			res = self._canonical_prefix + name,
		)

		try:
			signature = self.credentials.sign_bytes(string_to_sign)
		except AttributeError:
			s = Signer(Request(), self.credentials, self.credentials.service_account_email)
			signature = s.sign(string_to_sign)

		return self._url(name) + "?" + urlencode(dict(
			GoogleAccessId = self.credentials.service_account_email,
			Expires = exp,
			Signature = b64encode(signature).decode('utf-8'),
		))

Storage = GoogleStorage
