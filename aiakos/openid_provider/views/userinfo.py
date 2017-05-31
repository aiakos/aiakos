from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from ..scopes import SCOPES
from ..userinfo import makeUserInfo


@method_decorator(csrf_exempt, name='dispatch') # for post
class UserInfoView(View):

	def dispatch(self, request):
		response = super().dispatch(request)
		response['Access-Control-Allow-Origin'] = '*'
		return response

	def get(self, request):
		if not request.user:
			return JsonResponse(dict(error='login_required'), status=401)

		"""http://openid.net/specs/openid-connect-core-1_0.html#UserInfo"""
		if hasattr(request, 'token') and request.token:
			info = makeUserInfo(request.user, request.token.client, request.token.scope)
		else:
			info = makeUserInfo(request.user, None, SCOPES.keys())

		return JsonResponse(info, status=200)

	def post(self, request):
		"""The UserInfo Endpoint MUST support the use of the HTTP GET and HTTP POST methods defined in RFC 2616 [RFC2616]."""
		return self.get(request)
