from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from django_extauth.models import *
from django_modular_user.admin import UserAdmin

from .models import User
from .openid_provider.models import *


class ClientInline(admin.StackedInline):
	model = Client
	extra = 0
	verbose_name = _("OpenID Client settings")
	verbose_name_plural = _("OpenID Client settings")

class ExternalIdentityInline(admin.TabularInline):
	model = ExternalIdentity
	extra = 0

class ExtendedUserAdmin(UserAdmin):
	inlines = UserAdmin.inlines + [ClientInline, ExternalIdentityInline]

admin.site.register(User, ExtendedUserAdmin)
