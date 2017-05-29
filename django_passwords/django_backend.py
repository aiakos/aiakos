from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError

from .models import PasswordBackend

User = get_user_model()

# True - allow
# False - deny (all following backends will get called with 'fakepassword', and their return values will be ignored)
# None - no opinion, continue to the next rule

# Note: We always need to execute the same full codepath, so that timing attacks won't be possible.

def _check_password(user, password):
	final_result = None

	for backend in PasswordBackend.objects.all():
		result = backend.check_password(user, password)

		if final_result == False:
			result = False

		if result == True:
			return True, backend

		if result == False:
			password = 'fakepassword'
			final_result = False

	return False, None

def check_password(user, password):
	result, backend = _check_password(user, password)

	if not result:
		return False

	if backend.copy_passwords_to:
		backend.copy_passwords_to.set_password(user, password)

	return True

class DjangoBackend(ModelBackend):
	def authenticate(self, request=None, user=None, user_id=None, username=None, password=None, **kwargs):
		if username is None:
			username = kwargs.get(User.USERNAME_FIELD)

		if username is not None:
			try:
				user = User._default_manager.get_by_natural_key(username)
			except User.DoesNotExist:
				pass

		if user_id is not None:
			try:
				user = User._default_manager.get(id=user_id)
			except (User.DoesNotExist, ValidationError):
				pass

		if check_password(user, password):
			if user and self.user_can_authenticate(user):
				return user
