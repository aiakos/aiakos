from django.contrib.auth.models import User


def can_reset_password(self):
	return self.has_usable_password() or len(self.externalidentity_set) == 0

User.can_reset_password = property(can_reset_password)
