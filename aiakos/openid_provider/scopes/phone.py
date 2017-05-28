from django.utils.translation import ugettext_lazy as _


class PhoneScope:
	name = _("Phone number")
	description = _("Access to your phone number.")

	def __init__(self, user=None):
		self.user = user

	@property
	def claims(self):
		# TODO Revisit after we add official support for phone numbers.
		return {
			'phone_number': self.user.phone_number,
			'phone_number_verified': True,
		}
