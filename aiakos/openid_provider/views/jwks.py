from django.http import JsonResponse
from django.views.generic import View

from Cryptodome.PublicKey import RSA
from jwkest import long_to_base64

from ..models import RSAKey


class JWKSView(View):

	def dispatch(self, request):
		response = super().dispatch(request)
		response['Access-Control-Allow-Origin'] = '*'
		return response

	def get(self, request):
		dic = dict(keys=[])

		for rsakey in RSAKey.objects.all():
			public_key = RSA.importKey(rsakey.key).publickey()
			dic['keys'].append({
				'kty': 'RSA',
				'alg': 'RS256',
				'use': 'sig',
				'kid': rsakey.kid,
				'n': long_to_base64(public_key.n),
				'e': long_to_base64(public_key.e),
			})

		return JsonResponse(dic)
