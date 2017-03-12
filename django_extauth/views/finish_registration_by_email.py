from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import View

from ..token import in_url_authentication

User = get_user_model()

@method_decorator(in_url_authentication, name='dispatch')
class FinishRegistrationByEmail(View):
	def get(self, request):
		ei = request.external_identity

		if not ei:
			raise Http404

		user = User.objects.get(id=request.token["user_id"])
		if user.last_login or ei.exists:
			raise access_denied()

		ei.user = user
		ei.trusted = True
		ei.save()

		auth_login(request, ei.user) # Because he can reset password and then log in anyway

		if ei.user.profile.email == ei.email:
			ei.user.profile.email_verified = True
			ei.user.profile.save()

		messages.success(request, _("Your email was confirmed."))
		return redirect(settings.HOME_URL)
