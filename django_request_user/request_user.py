from importlib import import_module

from django.contrib.auth.models import AnonymousUser
from django.conf import settings

class Anon(AnonymousUser):
	def __bool__(self):
		return False

try:
	backend_names = settings.REQUEST_USER_BACKENDS
except AttributeError:
	backend_names = [
		'django.contrib.auth',
	]

def import_object(path, def_name):
	try:
		mod, cls = path.split(':', 1)
	except ValueError:
		mod = path
		cls = def_name

	return getattr(import_module(mod), cls)

backends = [import_object(path, 'get_user') for path in backend_names]

def get_request_user(request):
	try:
		return request._user
	except AttributeError:
		for backend in backends:
			user = backend(request)
			if user:
				request._user = user
				return request._user

	return Anon()

def set_request_user(request, user):
	if user.is_authenticated:
		request._user = user
	else:
		request._user = None

request_user = property(get_request_user, set_request_user)
