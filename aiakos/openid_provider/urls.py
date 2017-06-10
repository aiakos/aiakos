from django.conf.urls import url

from . import views

app_name = 'openid_provider'

urlpatterns = [
	url(r'^\.well-known/openid-configuration$', views.ConfigurationView.as_view()),

	url(r'^oauth/authorize/$', views.AuthorizationView.as_view(), name='authorization'),
	url(r'^oauth/consent/$', views.ConsentView.as_view(), name='consent'),
	url(r'^oauth/token/$', views.TokenView.as_view(), name='token'),
	url(r'^oauth/userinfo/$', views.UserInfoView.as_view(), name='userinfo'),
	url(r'^oauth/jwks/$', views.JWKSView.as_view(), name='jwks'),
	url(r'^oauth/logout/$', views.LogoutView.as_view(), name='logout')
]
