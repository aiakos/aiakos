from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView


class SelectAccountView(TemplateView):
	template_name = 'registration/select_account.html'

	@property
	def login_url(self):
		return reverse('extauth:login')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['auth_request'] = self.request.flow.auth_request if self.request.flow else None
		context['login_url'] = self.login_url
		return context

	def get(self, request):
		if not request.user.accounts:
			return redirect(self.login_url)

		for acc in request.user.accounts:
			acc.__dict__['url'] = acc.url

		return super().get(request)
