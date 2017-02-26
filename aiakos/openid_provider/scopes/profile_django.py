from django.utils.translation import ugettext_lazy as _


class ProfileScope:
	name = _("Basic profile")
	description = _("Access to your basic information. Includes name and nickname.")

	def __init__(self, user=None):
		self.user = user

	@property
	def claims(self):
		return {
			'given_name': self.user.first_name,
			'family_name': self.user.last_name,
			'nickname': self.user.username,
			'profile': self.user.get_absolute_url(),
		}
