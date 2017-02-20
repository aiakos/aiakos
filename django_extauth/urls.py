from django.conf.urls import url

from . import views

app_name = 'extauth'

urlpatterns = [
	url(r'^login/(?P<provider>[^/]+)/$', views.login, name='begin'),
	url(r'^complete/(?P<provider>[^/]+)/$', views.complete, name='complete'),
	url(r'^$', views.IdentitiesView.as_view(), name='identities'),
]
