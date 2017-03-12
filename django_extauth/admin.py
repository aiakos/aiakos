from django.contrib import admin

from .models import *


class IdentityProviderAdmin(admin.ModelAdmin):
	list_display = ('domain', 'name', 'client_id', 'protocol')

admin.site.register(IdentityProvider, IdentityProviderAdmin)

class ExternalIdentityAdmin(admin.ModelAdmin):
	list_display = ('user', 'provider', 'sub')

admin.site.register(ExternalIdentity, ExternalIdentityAdmin)
