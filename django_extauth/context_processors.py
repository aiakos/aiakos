from .models import *

def identity_providers(request):
	return {
		'identity_providers': IdentityProvider.objects.all()
	}
