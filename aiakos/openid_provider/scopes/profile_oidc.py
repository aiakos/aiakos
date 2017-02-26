from django.utils.translation import ugettext_lazy as _


class ProfileScope:
	name = _("Basic profile")
	description = _("Access to your basic information. Includes names, gender, birthdate and other information.")

	def __init__(self, user=None):
		self.user = user

	@property
	def claims(self):
		return {
			'name': self.user.profile.name,
			'given_name': self.user.profile.given_name,
			'family_name': self.user.profile.family_name,
			'middle_name': self.user.profile.middle_name,
			'nickname': self.user.profile.nickname,
			'preferred_username': self.user.profile.preferred_username,
			'profile': self.user.profile.profile,
			'picture': self.user.profile.picture,
			'website': self.user.profile.website,
			'gender': self.user.profile.gender,
			'birthdate': self.user.profile.birthdate,
			'zoneinfo': self.user.profile.zoneinfo,
			'locale': self.user.profile.locale,
			'updated_at': self.user.profile.updated_at,
		}
