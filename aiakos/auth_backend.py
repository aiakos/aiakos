from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()

class BetterAuthBackend(ModelBackend):
	def authenticate(self, request=None, user=None, user_id=None, username=None, password=None, **kwargs):
		if username is None:
			username = kwargs.get(UserModel.USERNAME_FIELD)

		# We always want to do all queries (if everything is provided) so timing attacks won't be possible.
		if username:
			try:
				user = UserModel._default_manager.get_by_natural_key(username)
			except UserModel.DoesNotExist:
				pass

		if user_id:
			try:
				user = UserModel._default_manager.get(id=user_id)
			except UserModel.DoesNotExist:
				pass

		if user:
			if user.check_password(password) and self.user_can_authenticate(user):
				return user
		else:
			# Run the default password hasher once to reduce the timing
			# difference between an existing and a nonexistent user (#20760).
			UserModel().set_password(password)
