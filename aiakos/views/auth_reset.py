from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ..mail import send_mail
from .auth_links import password_reset_link

User = get_user_model()


class AuthResetForm(forms.Form):
	email = forms.EmailField(label=_("Email"), max_length=254)

	def process(self, request):
		email = self.cleaned_data['email']

		site = get_current_site(request)

		try:
			user = User.objects.get(email=email)
		except User.DoesNotExist:
			send_mail(email, 'registration/email/reset-404', {
				'log_in': 'https://' + site.domain + reverse('login')
			}, site=site)
		else:

			if user.can_reset_password:
				send_mail(user.email, 'registration/email/reset', {
					'user': user,
					'reset_password': password_reset_link(user, site),
				}, site=site)
			else:
				send_mail(user.email, 'registration/email/reset-not-allowed', {
					'user': user,
				}, site=site)

		return _("Check your e-mail.")
