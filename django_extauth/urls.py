from django.conf.urls import url
from django.contrib.auth import views as django_auth_views

from . import user, views

app_name = 'extauth'

urlpatterns = [
	url(r'^$', views.IdentitiesView.as_view(), name='identities'),

	url(r'^login/$', views.AuthView.as_view(), name='login'),
	url(r'^oauth-done/$', views.OAuthDoneView.as_view(), name='oauth-done'),

	url(r'^logout/$', django_auth_views.logout, name='logout'),

	url(r'^login/(?P<auth_token>[^/]+)/$', views.LoginByEmail.as_view(), name='login-by-email'),
	url(r'^confirm-email/(?P<auth_token>[^/]+)/$', views.FinishRegistrationByEmail.as_view(), name='finish-registration-by-email'),
]

oauth_actions = {
	'login': views.AuthView,
	'associate': views.IdentitiesView,
}
