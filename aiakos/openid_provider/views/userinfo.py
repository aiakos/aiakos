from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from ..userinfo import makeUserInfo


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class UserInfoView(View):

	def get(self, request):
		"""http://openid.net/specs/openid-connect-core-1_0.html#UserInfo"""
		info = makeUserInfo(request.user, request.token.client, request.token.scope)

		response = JsonResponse(info, status=200)
		response['Access-Control-Allow-Origin'] = '*'
		response['Cache-Control'] = 'no-store'
		response['Pragma'] = 'no-cache'
		return response

	def post(self, request):
		"""The UserInfo Endpoint MUST support the use of the HTTP GET and HTTP POST methods defined in RFC 2616 [RFC2616]."""
		return self.get(request)
