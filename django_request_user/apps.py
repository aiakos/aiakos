from django.apps import AppConfig
from django.http import HttpRequest

class DjangoRequestUserConfig(AppConfig):
	name = 'django_request_user'

	def ready(self):
		from .request_user import request_user
		HttpRequest.user = request_user
