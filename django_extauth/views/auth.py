import json
import logging

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import resolve_url, reverse
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView

from aiakos.openid_provider.decorators import oauth_error_response
from aiakos.openid_provider.errors import *
from six.moves.urllib.parse import urlencode

from .auth_login import AuthLoginForm
from .auth_oauth import OAuthLoginForm
from .auth_register import AuthRegisterForm
from .auth_reset import AuthResetForm
from .ei import log_in

logger = logging.getLogger(__name__)

def get_success_url(request, state=None):
	"""Ensure the user-originating redirection URL is safe."""
	if state:
		redirect_to = state[REDIRECT_FIELD_NAME]
	else:
		redirect_to = request.POST.get(
			REDIRECT_FIELD_NAME,
			request.GET.get(REDIRECT_FIELD_NAME, '')
		)

	url_is_safe = is_safe_url(
		url=redirect_to,
		host=request.get_host()
	)
	if not url_is_safe:
		return resolve_url(settings.LOGIN_REDIRECT_URL)
	return redirect_to

def get_error_url(request, error):
	base = get_success_url(request)

	if '?' in base:
		return base + '&error=' + error
	else:
		return base + '?error=' + error

class AuthView(TemplateView):
	template_name = 'registration/auth.html'
	redirect_authenticated_user = False

	class LoginForm(AuthLoginForm):
		method = forms.CharField(widget = forms.HiddenInput(), required = True, initial = 'login')

	class RegisterForm(AuthRegisterForm):
		method = forms.CharField(widget = forms.HiddenInput(), required = True, initial = 'register')

	class ResetForm(AuthResetForm):
		method = forms.CharField(widget = forms.HiddenInput(), required = True, initial = 'reset')

	class OAuthForm(OAuthLoginForm):
		method = forms.CharField(widget = forms.HiddenInput(), required = True, initial = 'oauth')

	@method_decorator(sensitive_post_parameters())
	@method_decorator(csrf_protect)
	@method_decorator(never_cache)
	def dispatch(self, request, *args, **kwargs):
		if self.redirect_authenticated_user and self.request.user.is_authenticated:
			redirect_to = get_success_url(self.request)
			if redirect_to == self.request.path:
				raise ValueError(
					"Redirection loop for authenticated user detected. Check that "
					"your LOGIN_REDIRECT_URL doesn't point to a login page."
				)
			return HttpResponseRedirect(redirect_to)
		return super().dispatch(request, *args, **kwargs)

	@property
	def method(self):
		try:
			return self._method
		except:
			self._method = 'login'
			return self._method

	@property
	def login_form(self):
		try:
			return self._login_form
		except:
			self._login_form = self.LoginForm()
			return self._login_form

	@property
	def register_form(self):
		try:
			return self._register_form
		except:
			self._register_form = self.RegisterForm()
			return self._register_form

	@property
	def reset_form(self):
		try:
			return self._reset_form
		except:
			self._reset_form = self.ResetForm()
			return self._reset_form

	@property
	def oauth_form(self):
		try:
			return self._oauth_form
		except:
			self._oauth_form = self.OAuthForm()
			return self._oauth_form

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update({
			REDIRECT_FIELD_NAME: get_success_url(self.request),
			'method': self.method,
			'login_form': self.login_form,
			'register_form': self.register_form,
			'reset_form': self.reset_form,
			'oauth_form': self.oauth_form,
		})
		return context

	def get_request_form(self, request):
		method = request.POST.get('method')

		if method == 'login':
			return 'login', self.LoginForm(data=request.POST)
		elif method == 'register':
			return 'register', self.RegisterForm(data=request.POST)
		elif method == 'reset':
			return 'reset', self.ResetForm(data=request.POST)
		elif method == 'oauth':
			return 'oauth', self.OAuthForm(data=request.POST)
		elif method == 'cancel':
			return 'cancel', None

		return None, None

	def post(self, request):
		if request.META.get('HTTP_ACCEPT') == 'application/json':
			return self.post_json(request)
		else:
			return self.post_ui(request)

	def post_ui(self, request):
		method, form = self.get_request_form(request)

		if method == 'cancel':
			return HttpResponseRedirect(get_error_url(self.request, 'access_denied'))

		if form:
			if form.is_valid():
				resp = form.process(request)

				if isinstance(resp, HttpResponseRedirect):
					return resp
				else:
					messages.success(request, resp)

				if hasattr(form, 'user') and form.user:
					return HttpResponseRedirect(get_success_url(self.request).replace('%7Bid%7D', str(form.user.pk)))
			else:
				self._method = method
				if method == 'login':
					self._login_form = form
				elif method == 'register':
					self._register_form = form
				elif method == 'reset':
					self._reset_form = form
				elif method == 'oauth':
					self._oauth_form = form

		return self.get(request)

	def post_api(self, request):
		method, form = self.get_request_form(request)

		resp = {}

		if method == 'cancel':
			resp['redirect'] = get_error_url(self.requests, 'access_denied')
			return resp

		if not form:
			raise invalid_request("Missing method parameter.")

		if not form.is_valid():
			errors = json.loads(form.errors.as_json())

			ex = invalid_request(errors)
			if '__all__' in errors:
				for e in errors['__all__']:
					if e['code'] == 'invalid_login':
						ex = invalid_grant(errors)
						ex.status_code = 403

			raise ex

		form_resp = form.process(request)

		if isinstance(form_resp, HttpResponseRedirect):
			resp['redirect'] = form_resp['Location']
		else:
			resp['message'] = form_resp

		if not request.user.is_anonymous:
			resp['redirect'] = get_success_url(self.request)

		return resp

	@method_decorator(oauth_error_response(logger))
	def post_json(self, request):
		response = JsonResponse(self.post_api(request))
		response['Cache-Control'] = 'no-store'
		response['Pragma'] = 'no-cache'
		return response

	def oauth_callback(self, request, state):
		if request.external_identity:
			log_in(request)
			return HttpResponseRedirect(get_success_url(request, state))

		return HttpResponseRedirect(reverse('extauth:login') + '?' + urlencode({REDIRECT_FIELD_NAME: state[REDIRECT_FIELD_NAME]}))
