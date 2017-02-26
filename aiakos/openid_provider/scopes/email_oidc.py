from django.utils.translation import ugettext_lazy as _


class EmailScope:
	name = _("Email")
	description = _("Access to your email address.")

	def __init__(self, user=None):
		self.user = user

	@property
	def claims(self):
		return {
			'email': self.user.profile.email,
			'email_verified': self.user.profile.email_verified,
		}
