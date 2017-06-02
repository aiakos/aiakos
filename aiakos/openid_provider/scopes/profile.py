from django.utils.translation import ugettext_lazy as _


class ProfileScope:
	name = _("Basic profile")
	description = _("Access to your basic information.")

	def __init__(self, user=None):
		self.user = user

	@property
	def claims(self):
		return {name: value for name, value in {
			'name': getattr(self.user, 'name', None),
			'given_name': getattr(self.user, 'given_name', None),
			'family_name': getattr(self.user, 'family_name', None),
			'middle_name': getattr(self.user, 'middle_name', None),
			'nickname': getattr(self.user, 'nickname', None),
			'preferred_username': getattr(self.user, 'preferred_username', getattr(self.user, 'username', None)),
			'profile': getattr(self.user, 'profile', None),
			'picture': getattr(self.user, 'picture', None),
			'website': getattr(self.user, 'website', None),
			'gender': getattr(self.user, 'gender', None),
			'birthdate': getattr(self.user, 'birthdate', None),
			'zoneinfo': getattr(self.user, 'zoneinfo', None),
			'locale': getattr(self.user, 'locale', None),
		}.items() if value is not None}
