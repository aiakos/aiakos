from django.http import JsonResponse
from django.views.generic import View

from .. import jwt


class JWKSView(View):

	def dispatch(self, request):
		response = super().dispatch(request)
		response['Access-Control-Allow-Origin'] = '*'
		return response

	def get(self, request):
		return JsonResponse(jwt.myself.public_jwks)
