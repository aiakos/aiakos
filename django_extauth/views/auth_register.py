from django import forms
from django.contrib.auth import password_validation
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext_lazy as _

from django_sendmail import send_mail

from ..models import ExternalIdentity, create_user
from .auth_links import finish_registration_by_email_link, password_reset_link


class AuthRegisterForm(forms.Form):
	email = forms.EmailField(label=_("Email"), max_length=254, required=True)
	password = forms.CharField(
		label=_("Password"),
		strip=False,
		widget=forms.PasswordInput,
		help_text=password_validation.password_validators_help_text_html(),
	)

	def process(self, request):
		email = self.cleaned_data['email']
		password = self.cleaned_data['password']

		site = get_current_site(request)

		try:
			ei = ExternalIdentity.objects.get(email=email)
		except ExternalIdentity.DoesNotExist:
			username, domain = email.split('@', 1)
			user = create_user(username)
			user.set_password(password)
			user.save()

			send_mail(email, 'registration/email/welcome', {
				'user': user,
				'email': email,
				'confirm_email': finish_registration_by_email_link(site, email, user),
			}, request=request)
			# Note: We can't log in here, as we can't log in in the 'else' case,
			# and it would tell the attacker if this e-mail is in the database
		else:

			if ei.trusted:
				send_mail(ei.email, 'registration/email/welcome-back', {
					'user': ei.user,
					'reset_password': password_reset_link(site, ei.email, ei.user),
				}, request=request)
			else:
				send_mail(ei.email, 'registration/email/welcome-back', {
					'user': ei.user,
				}, request=request)

		return _("Check your e-mail.")
