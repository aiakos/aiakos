"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.conf.urls import url, include
	2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView, TemplateView

from django_extauth import v1 as auth_v1
from rest_framework import routers

from .openid_provider import v1 as oauth_v1

v1 = routers.DefaultRouter()
v1.register(r'clients', oauth_v1.ClientViewSet)
v1.register(r'accounts', auth_v1.AccountViewSet, base_name='account')

urlpatterns = [
	url(r'^v1/', include(v1.urls)),

	url(r'^$', login_required(RedirectView.as_view(url=settings.HOME_URL)), name='home'),

	url(r'^admin/', admin.site.urls),

	url(r'^', include('django_extauth.urls', namespace='extauth')),

	url(r'^', include('aiakos.openid_provider.urls', namespace='openid_provider')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
