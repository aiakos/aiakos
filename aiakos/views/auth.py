import json
import logging

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import resolve_url
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView

from aiakos.openid_provider.decorators import oauth_error_response
from aiakos.openid_provider.errors import *

from .auth_login import AuthLoginForm
from .auth_register import AuthRegisterForm
from .auth_reset import AuthResetForm

logger = logging.getLogger(__name__)

# Backport from Django 1.11
class SuccessURLAllowedHostsMixin:
	success_url_allowed_hosts = set()

	def get_success_url_allowed_hosts(self):
		allowed_hosts = {self.request.get_host()}
		allowed_hosts.update(self.success_url_allowed_hosts)
		return allowed_hosts


class AuthView(SuccessURLAllowedHostsMixin, TemplateView):
	redirect_field_name = REDIRECT_FIELD_NAME
	template_name = 'registration/auth.html'
	redirect_authenticated_user = True

	class LoginForm(AuthLoginForm):
		method = forms.CharField(widget = forms.HiddenInput(), required = True, initial = 'login')

	class RegisterForm(AuthRegisterForm):
		method = forms.CharField(widget = forms.HiddenInput(), required = True, initial = 'register')

	class ResetForm(AuthResetForm):
		method = forms.CharField(widget = forms.HiddenInput(), required = True, initial = 'reset')

	@method_decorator(sensitive_post_parameters())
	@method_decorator(csrf_protect)
	@method_decorator(never_cache)
	def dispatch(self, request, *args, **kwargs):
		if self.redirect_authenticated_user and self.request.user.is_authenticated:
			redirect_to = self.get_success_url()
			if redirect_to == self.request.path:
				raise ValueError(
					"Redirection loop for authenticated user detected. Check that "
					"your LOGIN_REDIRECT_URL doesn't point to a login page."
				)
			return HttpResponseRedirect(redirect_to)
		return super().dispatch(request, *args, **kwargs)

	def get_success_url(self):
		"""Ensure the user-originating redirection URL is safe."""
		redirect_to = self.request.POST.get(
			self.redirect_field_name,
			self.request.GET.get(self.redirect_field_name, '')
		)
		url_is_safe = is_safe_url(
			url=redirect_to,
			host=list(self.get_success_url_allowed_hosts())[0]
		)
		if not url_is_safe:
			return resolve_url(settings.LOGIN_REDIRECT_URL)
		return redirect_to

	def get_error_url(self, error):
		base = self.get_success_url()

		if '?' in base:
			return base + '&error=' + error
		else:
			return base + '?error=' + error

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

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update({
			self.redirect_field_name: self.get_success_url(),
			'method': self.method,
			'login_form': self.login_form,
			'register_form': self.register_form,
			'reset_form': self.reset_form,
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
			return HttpResponseRedirect(self.get_error_url('access_denied'))

		if form:
			if form.is_valid():
				msg = form.process(request)

				if msg:
					messages.success(request, msg)

				if request.user:
					return HttpResponseRedirect(self.get_success_url())
			else:
				self._method = method
				if method == 'login':
					self._login_form = form
				elif method == 'register':
					self._register_form = form
				elif method == 'reset':
					self._reset_form = form

		return self.get(request)

	def post_api(self, request):
		method, form = self.get_request_form(request)

		resp = {}

		if method == 'cancel':
			resp['redirect'] = self.get_error_url('access_denied')
			return resp

		if not form:
			raise invalid_request("Missing method parameter.")

		if not form.is_valid():
			errors = json.loads(form.errors.as_json())

			e_class = invalid_request
			if '__all__' in errors:
				for e in errors['__all__']:
					if e['code'] == 'invalid_login':
						e_class = invalid_grant

			raise e_class(errors)

		msg = form.process(request)

		if msg:
			resp['message'] = msg

		if not request.user.is_anonymous:
			resp['redirect'] = self.get_success_url()

		return resp

	@method_decorator(oauth_error_response(logger))
	def post_json(self, request):
		response = JsonResponse(self.post_api(request))
		response['Cache-Control'] = 'no-store'
		response['Pragma'] = 'no-cache'
		return response
