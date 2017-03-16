from django.http import JsonResponse

from .errors import *


def oauth_error_response(logger):
	def Middleware(get_response):
		def middleware(request, *args, **kwargs):
			try:
				return get_response(request, *args, **kwargs)
			except OAuthError as e:
				logger.debug("OAuth error", exc_info=True)
				response = JsonResponse({
					'error': type(e).__name__,
					'error_description': e.description,
				}, status=e.status_code)
				response['Cache-Control'] = 'no-store'
				response['Pragma'] = 'no-cache'
				return response

		return middleware
	return Middleware
