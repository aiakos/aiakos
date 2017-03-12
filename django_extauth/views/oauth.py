import json
from base64 import b64decode, b64encode

from django.shortcuts import redirect
from django.views import View

from ..models import ExternalIdentity, IdentityProvider


def authorize(provider, request, action, state=None):
	if not state:
		state = {}

	state = dict(
		provider = provider.domain,
		action = action,
		**state
	)

	state = b64encode(json.dumps(state).encode('utf-8'))

	return redirect(provider.client.authorize(
		redirect_uri = provider.redirect_uri(request),
		state = state,
		scope = ['openid', 'profile', 'email'],
	))


class OAuthDoneView(View):
	def _authenticate(self, request, state):
		request.external_identity = None

		try:
			provider = IdentityProvider.objects.get(domain=state['provider'])
			code = request.GET['code']
		except (KeyError, IdentityProvider.DoesNotExist):
			return

		res = provider.client.request_token(
			redirect_uri = provider.redirect_uri(request),
			code = code,
		)

		# TODO check nonce

		ei = ExternalIdentity.objects.forced_get(provider=provider, sub=res.id['sub'])
		ei.userinfo = res.id

		request.external_identity = ei

	def get(self, request):
		try:
			state = json.loads(b64decode(request.GET['state']).decode('utf-8'))
		except (json.JSONDecodeError, KeyError):
			raise Http404

		self._authenticate(request, state)

		from ..urls import oauth_actions
		view = oauth_actions[state['action']]()
		view.request = request
		return view.oauth_callback(request, state)
