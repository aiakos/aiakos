from django import forms
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django_sendmail import send_mail

from ..models import ExternalIdentity
from .auth_links import password_reset_link


class AuthResetForm(forms.Form):
	email = forms.EmailField(label=_("Email"), max_length=254, required=True)

	def process(self, request):
		email = self.cleaned_data['email']

		site = get_current_site(request)

		try:
			ei = ExternalIdentity.objects.get(email=email)
		except ExternalIdentity.DoesNotExist:
			send_mail(email, 'registration/email/reset-404', {
				'log_in': 'https://' + site.domain + reverse('extauth:login')
			}, site=site)
		else:

			if ei.trusted:
				send_mail(ei.email, 'registration/email/reset', {
					'user': ei.user,
					'reset_password': password_reset_link(site, ei.email),
				}, site=site)
			else:
				send_mail(ei.email, 'registration/email/reset-not-allowed', {
					'user': ei.user,
				}, site=site)

		return _("Check your e-mail.")
