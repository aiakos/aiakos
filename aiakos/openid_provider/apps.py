from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OpenIDProviderConfig(AppConfig):

	name = 'aiakos.openid_provider'
	verbose_name = _("OpenID Provider")
