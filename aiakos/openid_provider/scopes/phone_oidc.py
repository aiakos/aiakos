from django.utils.translation import ugettext_lazy as _


class PhoneScope:
	name = _("Phone number")
	description = _("Access to your phone number.")

	def __init__(self, user=None):
		self.user = user

	@property
	def claims(self):
		return {
			'phone_number': self.user.profile.phone_number,
			'phone_number_verified': self.user.profile.phone_number_verified,
		}
