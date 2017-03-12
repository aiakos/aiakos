from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from ..models import ExternalIdentity


class AuthLoginForm(forms.Form):
	"""
	Base class for authenticating users. Extend this to get a form that accepts
	username/password logins.
	"""
	username = auth_forms.UsernameField(
		label=_("Username or email"),
		max_length=254,
		widget=forms.TextInput(attrs={'autofocus': True}),
	)
	password = forms.CharField(
		label=_("Password"),
		strip=False,
		widget=forms.PasswordInput,
	)

	error_messages = {
		'invalid_login': _(
			"Please enter a correct username and password. Note that both fields may be case-sensitive."
		),
	}

	def __init__(self, request=None, *args, **kwargs):
		self.request = request
		self.user = None
		super().__init__(*args, **kwargs)

	def clean(self):
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')
		user = None

		if username is not None and password:
			if '@' in username:
				try:
					user = ExternalIdentity.objects.get(email=username).user
					username = None
				except ExternalIdentity.DoesNotExist:
					pass

			self.user = authenticate(request=self.request, user=user, username=username, password=password)
			if self.user is None:
				raise forms.ValidationError(
					self.error_messages['invalid_login'],
					code='invalid_login',
				)

		return self.cleaned_data

	def process(self, request):
		auth_login(request, self.user)
