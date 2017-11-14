from django.shortcuts import redirect
from django.urls import reverse

from ..errors import *


def authorize(request):
	auth_request = request.flow.auth_request

	account_id = None

	try:
		account_id = request.resolver_match.kwargs['account_id']
	except KeyError:
		if not 'select_account' in auth_request.prompt:
			if auth_request.id_hint:
				account_id = auth_request.id_hint['sub']

	if not account_id in [str(acc.pk) for acc in request.user.accounts]:
		account_id = None

	if not account_id:
		if 'none' in auth_request.prompt:
			request.flow = None
			return auth_request.deny(interaction_required())

		return redirect(reverse('extauth:select-account'))

	return redirect(reverse('openid_provider:consent', args=[account_id]))
