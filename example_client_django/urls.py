from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
	url(r'^$', login_required(TemplateView.as_view(template_name='example.html'))),
	url(r'^accounts/login/', include('django_auth_oidc.urls')),
	url(r'^admin/', admin.site.urls),
]
