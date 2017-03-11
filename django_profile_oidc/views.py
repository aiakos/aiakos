from django.views.generic import DetailView

from django.contrib.auth import get_user_model

class ProfileView(DetailView):
	model = get_user_model()
	template_name = "registration/profile.html"

	slug_url_kwarg = 'username'
	slug_field = 'username'
	context_object_name = 'profile'
