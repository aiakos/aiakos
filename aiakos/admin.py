from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from django_extauth.models import *
from django_profile_oidc.models import *

from .openid_provider.models import *


class ClientInline(admin.StackedInline):
	model = Client
	extra = 0
	verbose_name = _("OpenID Client settings")
	verbose_name_plural = _("OpenID Client settings")

class ProfileInline(admin.StackedInline):
	model = Profile
	extra = 0
	verbose_name = _("profile")
	verbose_name_plural = _("profile")

class ExternalIdentityInline(admin.TabularInline):
	model = ExternalIdentity
	extra = 0

class ExtendedUserAdmin(UserAdmin):
	inlines = UserAdmin.inlines + [ClientInline, ProfileInline, ExternalIdentityInline]
	fieldsets = (
		(None, {'fields': ('username', 'email', 'password', 'date_joined', 'last_login')}),
		(_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
	)

admin.site.unregister(User)
admin.site.register(User, ExtendedUserAdmin)
