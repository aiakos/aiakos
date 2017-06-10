from django.apps import AppConfig
from django.contrib import auth as django_auth


class DjangoMultiuserConfig(AppConfig):
	name = 'aiakos.multiuser'

	def ready(self):
		from .auth import get_user, login
		django_auth.get_user = get_user
		django_auth.login = login
