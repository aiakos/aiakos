from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import *

Account = get_user_model()

class ServiceAccountInline(admin.TabularInline):
	model = Account
	extra = 0
	fields = ['id', 'is_active', 'oauth_application_type', 'oauth_auth_method', '_oauth_redirect_uris', '_oauth_post_logout_redirect_uris', 'oauth_allow_wildcard_redirect']
	readonly_fields = ['id']

class AppAdmin(admin.ModelAdmin):
	inlines = [ServiceAccountInline]

admin.site.register(App, AppAdmin)
admin.site.register(UserConsent)
admin.site.register(RSAKey)
