from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from aiakos.flow import Flow

from .oauth_request import EndSessionRequest, badrequest_handler


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(badrequest_handler, name='dispatch')
class EndSessionView(View):

	def _handle(self, request, data):
		request.flow = Flow()
		request.flow.auth_request = EndSessionRequest.parse(data)

		return redirect(reverse('openid_provider:logout'))

	def get(self, request):
		return self._handle(request, request.GET)
