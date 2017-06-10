from django.conf.urls import url
from django.contrib.auth import views as django_auth_views

from . import user, views

app_name = 'extauth'

urlpatterns = [
	url(r'^u/(?P<user_id>[^/]+)/auth/settings/$', views.SettingsView.as_view(), name='settings'),

	url(r'^auth/login/$', views.AuthView.as_view(), name='login'),
	url(r'^auth/oauth-done/$', views.OAuthDoneView.as_view(), name='oauth-done'),

	url(r'^auth/logout/$', django_auth_views.logout, name='logout'),

	url(r'^auth/login/(?P<auth_token>[^/]+)/$', views.LoginByEmail.as_view(), name='login-by-email'),
	url(r'^auth/confirm-email/(?P<auth_token>[^/]+)/$', views.FinishRegistrationByEmail.as_view(), name='finish-registration-by-email'),
]

oauth_actions = {
	'login': views.AuthView,
	'associate': views.SettingsView,
}
