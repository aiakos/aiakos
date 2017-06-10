from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import is_valid_path


def PrependUser(get_response):
	def prepend_user(request):
		urlconf = getattr(request, 'urlconf', None)

		try:
			account = request.user.default
		except AttributeError:
			account = request.user

		if account:
			prefix = '/u/{}'.format(request.user.pk)
		else:
			prefix = '/u/0'

		if not request.path.startswith('/u/'):
			if not is_valid_path(request.path_info, urlconf) and is_valid_path(prefix + request.path_info, urlconf):

				if account:
					resp = HttpResponse(status=307)
					resp['Location'] = prefix + request.get_full_path()
				else:
					resp = HttpResponse(status=303)
					resp['Location'] = settings.LOGIN_URL

				return resp

		return get_response(request)
	return prepend_user
