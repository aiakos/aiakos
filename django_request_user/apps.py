from django.apps import AppConfig
from django.http import HttpRequest
from rest_framework.request import Request

class DjangoRequestUserConfig(AppConfig):
	name = 'django_request_user'

	def ready(self):
		from .request_user import request_user, drf_request_user
		HttpRequest.user = request_user
		Request.user = drf_request_user
