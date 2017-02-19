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
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from oidc_provider.views import ProviderInfoView

urlpatterns = [
	url(r'^$', login_required(TemplateView.as_view(template_name='home.html')), name='home'),
	url(r'^admin/', admin.site.urls),
	url(r'^accounts/', include('django.contrib.auth.urls')),
	url(r'^accounts/', include('django_extauth.urls', namespace='extauth')),
	url(r'^openid/', include('oidc_provider.urls', namespace='oidc_provider')),
	url(r'^\.well-known/openid-configuration/$', ProviderInfoView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
