from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView

from .auth_login import AuthLoginForm
from .auth_register import AuthRegisterForm
from .auth_reset import AuthResetForm


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

	def post(self, request):
		if "cancel" in request.POST:
			return HttpResponseRedirect(self.get_success_url() + "&error=access_denied")

		self._method = request.POST.get('method')

		form = None
		if self.method == 'login':
			form = self._login_form = self.LoginForm(data=request.POST)
		elif self.method == 'register':
			form = self._register_form = self.RegisterForm(data=request.POST)
		elif self.method == 'reset':
			form = self._reset_form = self.ResetForm(data=request.POST)

		if form and form.is_valid():
			msg = form.process(request)
			if msg:
				messages.success(request, msg)

			if request.user:
				return HttpResponseRedirect(self.get_success_url())
			else:
				if self.method == 'login':
					del self._login_form
				if self.method == 'register':
					del self._register_form
				if self.method == 'reset':
					del self._reset_form
				self._method = 'login'

		return self.get(request)
