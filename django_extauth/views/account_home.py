from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import View

from aiakos.openid_provider.flows import authorize

Account = get_user_model()


class AccountHomeView(View):

	def dispatch(self, request, account_id):
		try:
			self.account = Account.objects.get(pk=account_id)
		except Account.DoesNotExist:
			raise Http404()

		return super().dispatch(request)

	def get(self, request):
		if request.flow:
			# TODO don't hardcode which flow to use
			return authorize(request)

		return redirect(reverse('extauth:account-settings', args=[self.account.id]))
