from django.conf.urls import url
from django.contrib.auth import get_user_model

from . import views, models

urlpatterns = [
	url(r'^(?P<username>[^/]+)/$', views.ProfileView.as_view(), name='profile'),
]

User = get_user_model()
User.profile = property(models.user_profile)
