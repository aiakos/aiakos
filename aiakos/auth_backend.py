from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()

class UsernameOrEmailBackend(ModelBackend):
	def authenticate(self, request=None, username=None, email=None, password=None, **kwargs):
		if username is None:
			username = kwargs.get(UserModel.USERNAME_FIELD)

		if email is None:
			if "@" in username:
				email = username
				username = None

		user = None

		# We always want to do 2 queries (if both username and email provided)
		# so timing attacks won't be possible.
		# Do email first, so that username will override it if user is found.
		if email:
			try:
				user = UserModel._default_manager.get(email=email)
			except UserModel.DoesNotExist:
				pass
			except UserModel.MultipleObjectsReturned: # email is not unique in standard Django
				pass

		if username:
			try:
				user = UserModel._default_manager.get_by_natural_key(username)
			except UserModel.DoesNotExist:
				pass

		if user:
			if user.check_password(password) and self.user_can_authenticate(user):
				return user
		else:
			# Run the default password hasher once to reduce the timing
			# difference between an existing and a nonexistent user (#20760).
			UserModel().set_password(password)
