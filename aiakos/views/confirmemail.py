from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import View

from ..tokens import expandEmailConfirmationToken


class EmailConfirmationView(View):
	def get(self, request, token):
		data = expandEmailConfirmationToken(token)
		if not data:
			raise Http404

		if data.user.profile.email != data.email:
			raise Http404

		data.user.profile.email_verified = True
		data.user.profile.save()
		data.user.email = data.email
		data.user.save()

		messages.success(request, _("Your email was confirmed."))
		return redirect(settings.HOME_URL)
