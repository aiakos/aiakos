from django.contrib.auth import get_user_model

User = get_user_model()

class Backend:
	def __init__(self, url):
		pass

	def check_password(self, user, password):
		if user and user.has_usable_password():
			return user.check_password(password)
		else:
			User().check_password(password)
			return None

	def set_password(self, user, password):
		user.set_password(password)
		user.save(update_fields=['password'])
