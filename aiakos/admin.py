from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from django_extauth.models import *
from django_modular_user.admin import UserAdmin

from .models import User
from .openid_provider.models import *


class ExternalIdentityInline(admin.TabularInline):
	model = ExternalIdentity
	extra = 0

class ExtendedUserAdmin(UserAdmin):
	inlines = UserAdmin.inlines + [ExternalIdentityInline]

admin.site.register(User, ExtendedUserAdmin)
