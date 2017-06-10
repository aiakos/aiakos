from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from ..errors import account_selection_required
from .auth_request import AuthRequest


class SelectAccountView(TemplateView):
	template_name = 'openid_provider/select_account.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['auth_request'] = self.auth_request
		context['login_url'] = self.login_url
		return context

	def consent_url(self, account_id=None):
		if not account_id:
			account_id = '{id}'
		return reverse('openid_provider:consent', args=[account_id]) + '?request=' + self.auth_request.id

	@property
	def login_url(self):
		return redirect_to_login(self.consent_url())['Location']

	def get(self, request):
		self.auth_request = AuthRequest(request)

		self.prompt = self.auth_request['prompt'].split(' ')

		self.account = None

		try:
			if 'select_account' in self.prompt:
				raise account_selection_required()

			if self.auth_request.id_hint:
				# TODO maybe check if id_hint_valid?
				sub = req.id_hint['sub']
				for acc in request.user.accounts:
					if str(acc.pk) == sub:
						self.account = acc

			# TODO maybe set self.account if there is only one logged in account
			# Google does that, but it may be confusing.

			if not self.account:
				raise account_selection_required()

		except account_selection_required:
			if 'none' in self.prompt:
				return self.auth_request.deny(interaction_required())

			if not request.user.accounts:
				return redirect(self.login_url)

			for acc in request.user.accounts:
				acc.consent_url = self.consent_url(acc.pk)

			return super().get(request)

		return redirect(self.consent_url(self.account.pk))
