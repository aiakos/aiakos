from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm


class AuthLoginForm(AuthenticationForm):
	def process(self, request):
		auth_login(request, self.get_user())
