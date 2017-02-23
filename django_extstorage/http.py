from django.conf import settings
from django.core.files.storage import Storage
from django.utils.functional import cached_property

from requests import Session

try:
	from urllib.parse import urljoin
except ImportError:
	from urlparse import urljoin

class HTTPStorage(Storage):
	def __init__(self, base_url=None):
		self._base_url = base_url

		if not self._session:
			self._session = Session()

	def _value_or_setting(self, value, setting):
		return setting if value is None else value

	@cached_property
	def base_url(self):
		if self._base_url is not None and not self._base_url.endswith('/'):
			self._base_url += '/'
		return self._value_or_setting(self._base_url, settings.MEDIA_URL)

	def _url(self, name):
		url = urljoin(self.base_url, name.lstrip("/"))
		assert(url.startswith(self.base_url))
		return url

	def url(self, name):
		return self._url(name)

	def delete(self, name):
		self._session.delete(self._url(name))

	def exists(self, name):
		r = self._session.head(self._url(name))
		if r.status_code >= 200 and r.status_code < 300:
			return True
		if r.status_code == 404:
			return False
		r.raise_for_status()

	def _save(self, name, content):
		self._session.put(self._url(name), data=content)
		return name

	def _open(name, mode='rb'):
		raise NotImplementedError() # TODO

Storage = HTTPStorage
