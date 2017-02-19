from django.contrib import admin

from .models import *

class IdentityProviderAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug': ('name',)}
	list_display = ('name', 'slug', 'url', 'client_id', 'legacy_protocol')

admin.site.register(IdentityProvider, IdentityProviderAdmin)

class ExternalIdentityAdmin(admin.ModelAdmin):
	list_display = ('user', 'provider', 'sub')

admin.site.register(ExternalIdentity, ExternalIdentityAdmin)
