from django.utils.cache import patch_vary_headers

class RequestHeaders:
	def __init__(self, META):
		self.META = META
		self.used = set()

	def __getattr__(self, header):
		self.used.add(header.lower())
		return self.META.get('HTTP_' + header.upper())

class HeadersMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		request.headers = RequestHeaders(request.META)
		response = self.get_response(request)
		patch_vary_headers(response, request.headers.used)
		return response
