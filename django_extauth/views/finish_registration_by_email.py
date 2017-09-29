import json
import logging

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView

from aiakos.openid_provider.decorators import oauth_error_response
from aiakos.openid_provider.errors import *

from ..token import in_url_authentication

logger = logging.getLogger(__name__)


class FinishRegistrationForm(forms.Form):
	email = forms.EmailField(label=_("Email"), disabled=True)
	password = forms.CharField(
		label=_("Password"),
		strip=False,
		widget=forms.PasswordInput,
	)

	error_messages = {
		'invalid_login': _(
			"Please enter a correct password. Note that it is case-sensitive."
		),
	}

	def __init__(self, request=None, user=None, *args, **kwargs):
		self.request = request
		self.user = user
		kwargs['initial'] = dict(email=request.external_identity.email)
		super().__init__(*args, **kwargs)

	def clean(self):
		password = self.cleaned_data.get('password')
		user = None

		if password:
			self.user = authenticate(request=self.request, user=self.user, password=password)
			if self.user is None:
				raise forms.ValidationError(
					self.error_messages['invalid_login'],
					code='invalid_login',
				)

		return self.cleaned_data

	def process(self, request):
		ei = request.external_identity

		ei.user = self.user
		ei.trusted = True
		ei.save()

		auth_login(request, ei.user) # Because he can reset password and then log in anyway

		return _("Your email was confirmed.")

User = get_user_model()

@method_decorator(in_url_authentication, name='dispatch')
class FinishRegistrationByEmail(TemplateView):
	template_name = 'registration/finish_registration.html'

	def dispatch(self, request):
		ei = request.external_identity

		if not ei:
			raise Http404

		if ei.exists:
			if request.user == ei.user or request.token["user_id"] == ei.user.id:
				messages.success(request, _("Your email addres has been confirmed before."))
				return redirect(settings.HOME_URL)
			else:
				messages.error(request, _("Link expired."))
				return redirect(settings.HOME_URL)

		user = User.objects.get(id=request.token["user_id"])
		if user.last_login:
			# You can't finish registration after logging in.
			messages.error(request, _("Link expired."))
			return redirect(settings.HOME_URL)

		return super().dispatch(request, user)

	@property
	def form(self):
		try:
			return self._form
		except AttributeError:
			self._form = FinishRegistrationForm(self.request)
			return self._form

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update(dict(
			form = self.form,
		))
		return context

	def post(self, request, user):
		if request.META.get('HTTP_ACCEPT') == 'application/json':
			return self.post_json(request, user)
		else:
			return self.post_ui(request, user)

	def post_ui(self, request, user):
		self._form = FinishRegistrationForm(request, user=user, data=request.POST)

		if not self._form.is_valid():
			return self.get(request, user)

		resp = self._form.process(request)

		messages.success(request, resp)
		return redirect(settings.HOME_URL)

	def post_api(self, request, user):
		self._form = FinishRegistrationForm(request, user=user, data=request.POST)

		if not self.form.is_valid():
			errors = json.loads(self.form.errors.as_json())

			e_class = invalid_request
			if '__all__' in errors:
				for e in errors['__all__']:
					if e['code'] == 'invalid_login':
						e_class = access_denied

			raise e_class(errors)

		resp = {}
		resp['message'] = self.form.process(request)
		return resp

	@method_decorator(oauth_error_response(logger))
	def post_json(self, request, user):
		response = JsonResponse(self.post_api(request, user))
		response['Cache-Control'] = 'no-store'
		response['Pragma'] = 'no-cache'
		return response
