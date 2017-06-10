from django.conf.urls import url

from . import views

app_name = 'multiuser'

urlpatterns = [
	url(r'^(?!u/).*$', views.prepend_user)
]
