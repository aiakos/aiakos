from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _

from ..models import create_user

SAFE_FIELDS = ['name', 'nickname']

def pull_userdata_from(ei):
	for field in SAFE_FIELDS:
		if not getattr(ei.user, field):
			newval = ei.userinfo.get(field)
			if newval:
				setattr(ei.user, field, newval)

	if ei.provider.inherit_admin_status and ei.userinfo.get('openid-connect-python/is_admin', False):
		ei.user.is_staff = True
		ei.user.is_superuser = True

	ei.user.save()

	for ai in ei.additional_identities:
		if not ai.exists:
			ai.user = ei.user
			ai.save()


@login_required
def associate(request):
	ei = request.external_identity

	if ei.exists:
		if request.user == ei.user:
			messages.info(request, _("This identity is already connected to your account."))
			pull_userdata_from(ei)
		else:
			messages.error(request, _("This identity is already connected to another account."))
	else:
		ei.user = request.user
		ei.save()
		pull_userdata_from(ei)


def log_in(request):
	ei = request.external_identity

	if ei.exists:
		if ei.trusted:
			auth.login(request, ei.user)
			pull_userdata_from(ei)
		else:
			messages.error(request, _("You have disabled logging in with this identity."))
	else:
		ais_of_other_users = [ai for ai in ei.additional_identities if ai.exists]

		if ais_of_other_users:
			# TODO Ask user if he wants to merge accounts (=> log in with another) or create a new one
			pass

		username = ei.userinfo.get('preferred_username')
		if not username:
			username = ei.userinfo.get('nickname')
		if not username:
			username = ei.userinfo.get('name')
		if not username:
			username = ei.userinfo['sub']

		ei.user = create_user(username)
		ei.trusted = True
		ei.save()

		auth.login(request, ei.user)
		pull_userdata_from(ei)
