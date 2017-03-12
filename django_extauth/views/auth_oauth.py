from django import forms
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.translation import ugettext_lazy as _

from ..models import IdentityProvider
from .oauth import authorize


class OAuthLoginForm(forms.Form):
	provider = forms.ModelChoiceField(label=_("Provider"), required=True, queryset=IdentityProvider.objects.exclude(protocol=''), to_field_name='domain')

	def process(self, request):
		provider = self.cleaned_data['provider']

		return authorize(provider, request, 'login', {
			REDIRECT_FIELD_NAME: request.GET.get(REDIRECT_FIELD_NAME, ''),
		})
