"""
Use cases:
1. Aiakos as a public webapp login page (professional, not cat-photo-sharing app)
2. Aiakos as company intranet gateway - with ENABLE_PASSWORD_RESET=False, ENABLE_REGISTRATION=False, and no or only company-controlled external identities.

User visible flows:
- Sign in with password
- Register with password
- Sign in with external -> might create account

Goals:
1. We want 100% security. Not 90%, and not 110%. (200% can still be achieved with the help of other layers.)
2. We don't want to answer if we have a given e-mail in the database.
3. We want to automatically merge accounts with the same e-mail.
4. We can tolerate email-less accounts. But we don't want them to be common.

Other things:
1. We're going to support 2FA for password-based logins. You're supposed to assume it's done as part of the check_password method - unless you see that it's going to be impossible.
2. We might want to support 2FA for everything, not only password-based logins. In that case, that's just another layer happening after request.user = user.
3. We're going to support logins with username instead of e-mail, but this is just a name-to-email layer happening before the flows.
4. We already have a layer with support for connecting new external identities when user is already logged in.
5. We can require admins to set additional properties on providers, like "owns_emails".
"""

class User:
	email = models.EmailField(unique=True)

class ExternalIdentity:
	provider = models.ForeignKey(Provider)
	sub = models.CharField()
	user = models.ForeignKey(User)

	class Meta:
		unique_together = [[provider, sub]]

def LogInWithEmailAndPassword(email, password):
	try:
		user = User.get(email=email)
	except:
		pass
	else:
		if user.check_password(password):
			request.user = user
			Show("You've logged in")
			return

	Show("Bad email/password")

@property
def can_reset_password(user):
	if not settings.ENABLE_PASSWORD_RESET or user.disabled_password_reset:
		return False

	return user.has_password or not user.external_identities
	# The second clause is for cases when somebody deletes a provider, but wants to preserve users.

def ResetForgottenPassword(email):
	try:
		user = User.get(email=email)
	except:
		pass
	else:
		if user.can_reset_password:
			Send(user.email, password_reset_link(user))
		else:
			Send(user.email, "You already have an account; log in with: " + str(user.external_identities) + "or" + ("password" if user.has_password))

	Show("Check e-mail")

def Register(email, password):
	if not settings.ENABLE_REGISTRATION:
		raise SuspiciousOperation()

	try:
		user = User.get(email=email)
	except:
		user = User.create(password=password)
		Send(email, email_confirmation_link(user, email))
		# Note: We can't log in here, as we can't log in in the "except" case,
		# and it would tell the attacker if this e-mail is in the database
	else:
		if user.can_reset_password:
			Send(user.email, password_change_confirmation_link(user, password))
		else:
			Send(user.email, "You already have an account; log in with: " + str(user.external_identities) + "or" + ("password" if user.has_password))

	Show("Registered, check e-mail")

def ExternalLogIn(ei: ExternalIdentity):
	try:
		user = ei.user
	else:
		request.user = user
	except:
		if not ei.provider.allow_registration:
			raise SuspiciousOperation()

		try:
			user = User.get(email=ei.email)
		else:
			if ei.provider.owns_emails # Like Google
				and user.can_reset_password:
				ei.user = user
				request.user = user
			else: # Like GitHub
				Ask user if he wants to merge accounts (=> log in with another first) or create a new one with no e-mail
				# Why?
				# Cause if user's GitHub account got hacked,
				# and he didn't authorize it in Aiakos,
				# we shouldn't let the hacker in.

				# Note: In this case we can expose the fact that we have
				# this email in the database, as the user has shown
				# quite a strong relationship with this email.
		except:
			user = User.create()
			if ei.email_verified:
				user.email = ei.email
			else:
				Send(email, email_confirmation_link(user, ei.email))
			request.user = user

def ConfirmEmail(user, email): # assumes that link authenticity was checked before
	user.email = email
	if user.can_reset_password:
		request.user = user # Because he can reset password and then log in anyway
