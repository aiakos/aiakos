from django.conf import settings
from django.contrib import auth
from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import redirect, resolve_url
from django.urls import reverse
from django.utils.http import is_safe_url

from .models import *
import uuid
import random

def login(request, provider):
	try:
		provider = IdentityProvider.objects.get(slug=provider)
	except IdentityProvider.DoesNotExist:
		raise Http404

	return_path = request.GET.get(auth.REDIRECT_FIELD_NAME, '')

	return redirect(provider.client.authorize(
		redirect_uri = request.build_absolute_uri(reverse('extauth:complete', args=[provider.slug])),
		state = return_path,
		scope = ['openid', 'profile', 'email'],
	))

def complete(request, provider):
	try:
		provider = IdentityProvider.objects.get(slug=provider)
	except IdentityProvider.DoesNotExist:
		raise Http404

	return_path = request.GET.get('state')

	res = provider.client.request_token(
		redirect_uri = request.build_absolute_uri(reverse('extauth:complete', args=[provider.slug])),
		code = request.GET['code'],
	)

	try:
		ei = ExternalIdentity.objects.get(provider=provider, sub=res.id['sub'])

		if request.user != ei.user:
			# TODO Think about adding an account merge form here (if not anonymous).
			auth.login(request, ei.user)

	except ExternalIdentity.DoesNotExist:
		if not request.user.is_authenticated:
			User = auth.get_user_model()

			base_username = res.id.get("preferred_username")
			if not base_username:
				base_username = res.id.get("nickname")
			if not base_username:
				base_username = res.id.get("name")
			if not base_username:
				# We've tried. Tell Provider admins to fix themselves.
				base_username = str(uuid.uuid4()).replace("-", "")[0:10]

			base_username = base_username[0:130] # Django has 150 char limit, we need shorter for retrying.

			username = base_username
			last_error = None
			for i in range(1, 11): # Try 10 times
				try:
					user = User.objects.create(username=username)
					break
				except IntegrityError as e:
					username = base_username + str(random.randrange(0, 10**i))
					last_error = e
			else:
				raise last_error

			auth.login(request, user)

		ei = ExternalIdentity.objects.create(user=request.user, provider=provider, sub=res.id['sub'])

	assert(request.user == ei.user)

	ei.userinfo = res.id
	ei.save()

	if 'django_profile_oidc' in settings.INSTALLED_APPS:
		# Yay!
		from django_profile_oidc.models import Profile

		p = Profile.from_dict(ei.userinfo)

		try:
			ei.user.profile
		except:
			p.user = ei.user
			p.save()
		else:
			ei.user.profile.fill_missing(p)
			ei.user.profile.save()
	else:
		# Meh.

		if not ei.user.email:
			if ei.userinfo.get("email_verified", False):
				ei.user.email = ei.userinfo.get("email", "")

		if not ei.user.first_name:
			ei.user.first_name = ei.userinfo.get("given_name", "")

		if not ei.user.last_name:
			ei.user.last_name = ei.userinfo.get("family_name", "")

	if provider.inherit_admin_status and ei.userinfo.get("openid-connect-python/is_admin", False):
		ei.user.is_staff = True
		ei.user.is_superuser = True

	ei.user.save()

	url_is_safe = is_safe_url(
		url = return_path,
		host = request.get_host(),
		#allowed_hosts = set(request.get_host()),
		#require_https = request.is_secure(),
	)
	if not url_is_safe:
		return redirect(resolve_url(settings.LOGIN_REDIRECT_URL))
	return redirect(return_path)
