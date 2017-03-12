from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from ..models import IdentityProvider
from .ei import associate
from .oauth import authorize


@method_decorator(login_required, name='dispatch')
class IdentitiesView(TemplateView):
	template_name = "registration/identities.html"

	def post(self, request):
		if 'connect' in request.POST:
			provider = IdentityProvider.objects.get(domain=request.POST['connect'])
			return authorize(provider, request, 'associate')

		if 'disconnect' in request.POST:
			ei = request.user.externalidentity_set.get(pk=int(request.POST['disconnect']))
			ei.delete()

		if 'trust' in request.POST:
			ei = request.user.externalidentity_set.get(pk=int(request.POST['trust']))
			ei.trusted = True
			ei.save()

		if 'untrust' in request.POST:
			ei = request.user.externalidentity_set.get(pk=int(request.POST['untrust']))
			ei.trusted = False
			ei.save()

		return redirect(reverse('extauth:identities'))

	@method_decorator(login_required)
	def oauth_callback(self, request, state):
		if request.external_identity:
			associate(request)

		return redirect(reverse('extauth:identities'))
