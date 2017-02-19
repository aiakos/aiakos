from django.conf.urls import url

from . import views

app_name = 'extauth'

urlpatterns = [
	url(r'^login/(?P<provider>[^/]+)/$', views.login, name='begin'),
	url(r'^complete/(?P<provider>[^/]+)/$', views.complete, name='complete'),
#	url(r'^disconnect/(?P<provider>[^/]+)/$', views.disconnect, name='disconnect'),
#	url(r'^disconnect/(?P<provider>[^/]+)/(?P<association_id>[^/]+)/$', views.disconnect, name='disconnect_individual'),
]
