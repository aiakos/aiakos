from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^authorize/$', views.SAMLAuthorizationView.as_view(), name='authorization'),
]
