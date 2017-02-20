from django.views.generic import DetailView

from django.contrib.auth.models import User

class ProfileView(DetailView):
	model = User
	template_name = "registration/profile.html"

	slug_url_kwarg = 'username'
	slug_field = 'username'
	context_object_name = 'profile'
