import json

from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView


class LogoutView(TemplateView):
	template_name = 'openid_provider/logout.html'

	def dispatch(self, request):
		return super().dispatch(request)

	def get(self, request):
		if request.user.is_authenticated:
			if not request.flow or not request.flow.auth_request or not request.flow.auth_request.id_hint_valid or request.flow.auth_request.id_hint['sub'] not in (str(acc.id) for acc in request.user.accounts):
				return super().get(request)

		return self.go(request)

	def post(self, request):
		return self.go(request)

	def go(self, request):
		if request.user.is_authenticated:
			logout(request)

		if not request.flow or not request.flow.auth_request or not request.flow.auth_request.redirect_uri:
			request.flow = None
			return redirect(settings.LOGOUT_REDIRECT_URL)

		return redirect(reverse('openid_provider:continue'))
