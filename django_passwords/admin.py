from django.contrib import admin

from .models import *


class PasswordBackendAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'order', 'url', 'copy_passwords_to')
	list_editable = ('order', 'url', 'copy_passwords_to')

admin.site.register(PasswordBackend, PasswordBackendAdmin)
