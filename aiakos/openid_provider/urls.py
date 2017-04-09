from django.conf.urls import url

from . import views

app_name = 'openid_provider'

urlpatterns = [
	url(r'^authorize/$', views.AuthorizationView.as_view(), name='authorization'),
	url(r'^consent/$', views.ConsentView.as_view(), name='consent'),
	url(r'^token/$', views.TokenView.as_view(), name='token'),
	url(r'^userinfo/$', views.UserInfoView.as_view(), name='userinfo'),
	url(r'^jwks/$', views.JWKSView.as_view(), name='jwks'),
]
