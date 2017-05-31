
def challenge_to_string(scheme, params):
	s = scheme
	for name, value in params.items():
		s += ' {}="{}"'.format(name, value.replace('\\', '\\\\').replace('"', '\\"'))
	return s


class WWWAuthenticateMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		request.auth_challenges = []
		response = self.get_response(request)
		for i, challenge in enumerate(request.auth_challenges):
			whatever = 'WWW-Authenticate' + str(i)
			response._headers[whatever] = ('WWW-Authenticate', challenge_to_string(*challenge))
		return response
