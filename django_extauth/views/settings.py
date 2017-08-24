from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model, password_validation, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from ..models import IdentityProvider
from .ei import associate
from .oauth import authorize

User = get_user_model()


class SetPasswordForm(forms.Form):
	new_password = forms.CharField(
		label=_("New password"),
		widget=forms.PasswordInput,
		strip=False,
		help_text=password_validation.password_validators_help_text_html(),
	)

	def __init__(self, user, *args, **kwargs):
		self.user = user
		super().__init__(*args, **kwargs)

	def process(self, commit=True):
		password = self.cleaned_data["new_password"]
		self.user.set_password(password)
		if commit:
			self.user.save()
		return self.user


@method_decorator(login_required, name='dispatch')
class SettingsView(TemplateView):
	template_name = "registration/settings.html"

	@property
	def set_password_form(self):
		try:
			return self._set_password_form
		except:
			self._set_password_form = SetPasswordForm(self.request.user)
			return self._set_password_form

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['user'] = self.user
		context['set_password_form'] = self.set_password_form
		return context

	def dispatch(self, request, user_id):
		try:
			self.user = User.objects.get(pk=user_id)
		except User.DoesNotExist:
			raise Http404()

		return super().dispatch(request)

	@property
	def url(self):
		return reverse('extauth:settings', args=[self.user.id])

	def get(self, request):
		if not request.user.has_perm('django_extauth:view_user_settings', self.user):
			raise PermissionDenied()

		return super().get(request)

	def post(self, request):
		if not request.user.has_perm('django_extauth:change_user_settings', self.user):
			raise PermissionDenied()

		if 'connect' in request.POST:
			provider = IdentityProvider.objects.get(domain=request.POST['connect'])
			return authorize(provider, request, 'associate')

		if 'disconnect' in request.POST:
			ei = request.user.externalidentity_set.get(pk=int(request.POST['disconnect']))
			ei.delete()

		if 'trust' in request.POST:
			ei = request.user.externalidentity_set.get(pk=int(request.POST['trust']))
			ei.trusted = True
			ei.save()

		if 'untrust' in request.POST:
			ei = request.user.externalidentity_set.get(pk=int(request.POST['untrust']))
			ei.trusted = False
			ei.save()

		if 'set-password' in request.POST:
			self._set_password_form = SetPasswordForm(request.user, request.POST)
			if self._set_password_form.is_valid():
				update_session_auth_hash(request, request.user)
				messages.success(request, _("Your password has been changed."))

		return redirect(self.url)

	@method_decorator(login_required)
	def oauth_callback(self, request, state):
		if request.external_identity:
			associate(request)

		return redirect(self.url)
