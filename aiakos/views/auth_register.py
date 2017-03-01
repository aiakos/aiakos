from uuid import uuid4

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model, password_validation
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext_lazy as _

from django_profile_oidc.models import Profile

from ..mail import send_mail
from .auth_links import email_confirmation_link, password_reset_link

User = get_user_model()


class AuthRegisterForm(forms.ModelForm):
	email = forms.EmailField(label=_("Email"), required=True)
	password = forms.CharField(
		label=_("Password"),
		strip=False,
		widget=forms.PasswordInput,
		help_text=password_validation.password_validators_help_text_html(),
	)

	class Meta:
		model = User
		fields = ('email',)

	def process(self, request):
		userdata = self.save(commit=False)

		site = get_current_site(request)

		try:
			user = User.objects.get(email=userdata.email)
		except User.DoesNotExist:
			user = userdata
			user.username = str(uuid4())
			user.set_password(self.cleaned_data['password'])
			user.save()
			user.profile = Profile()
			user.profile.email = userdata.email
			user.profile.save()

			send_mail(user.profile.email, 'registration/email/welcome', {
				'user': user,
				'email': user.profile.email,
				'confirm_email': email_confirmation_link(user, user.profile.email, site),
			}, request=request)

			# Note: We can't log in here, as we can't log in in the 'else' case,
			# and it would tell the attacker if this e-mail is in the database
		else:

			if user.can_reset_password:
				send_mail(user.email, 'registration/email/welcome-back-reset', {
					'user': user,
					'reset_password': password_reset_link(user, site)
				}, request=request)
			else:
				send_mail(user.email, 'registration/email/welcome-back', {
					'user': user,
				}, request=request)

		messages.success(request, _("Check your e-mail."))
