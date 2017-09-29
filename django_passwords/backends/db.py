from django.contrib.auth import get_user_model


class Backend:
	def __init__(self, url):
		pass

	def check_password(self, user, password):
		ret = user.check_password(password)
		return ret if user.has_usable_password() else None

	def set_password(self, user, password):
		user.set_password(password)
		user.save(update_fields=['password'])
