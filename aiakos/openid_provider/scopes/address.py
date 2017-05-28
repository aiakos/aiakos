from django.utils.translation import ugettext_lazy as _


class AddressScope:
	name = _("Address information")
	description = _("Access to your address. Includes country, locality, street and other information.")

	def __init__(self, user=None):
		self.user = user

	@property
	def claims(self):
		return {
			'address': self.user.address,
		}
