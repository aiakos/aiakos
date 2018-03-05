from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views import View

from ..token import in_url_authentication
from .auth import get_success_url


class LoginByEmail(View):
	@method_decorator(in_url_authentication)
	def get(self, request, *args, **kwargs):
		redirect_to = get_success_url(self.request, request.external_identity.user.id)
		return HttpResponseRedirect(redirect_to)
