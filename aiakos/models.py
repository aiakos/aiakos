from django.contrib.auth.models import User


def can_reset_password(self):
	return self.has_usable_password() or self.externalidentity_set.count() == 0

User.can_reset_password = property(can_reset_password)
