from urllib.parse import urlsplit, urlunsplit

from django.core.exceptions import SuspiciousOperation
from django.conf import settings


BASE_ORIGIN = urlunsplit(urlsplit(settings.BASE_URL)._replace(path=''))
ALLOWED_ORIGINS = [BASE_ORIGIN]


class MissingOrigin(SuspiciousOperation):
	pass


class DisallowedOrigin(SuspiciousOperation):
	pass


class OriginMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):

		if request.headers.cookie and request.method != 'GET':
			origin = request.headers.origin
			if not origin:
				referer = request.headers.referer
				if referer:
					origin = urlunsplit(urlsplit(referer)._replace(path='', query=''))

			if not origin:
				raise MissingOrigin()

			if origin not in ALLOWED_ORIGINS:
				raise DisallowedOrigin()

		return self.get_response(request)
