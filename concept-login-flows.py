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
	user = models.ForeignKey(User)

	sub = models.CharField()
	provider = models.ForeignKey(Provider)

	@property
	def email(self):
		return self.sub + '@' + self.provider.url.replace(scheme='')

	class Meta:
		unique_together = [[provider, sub]]

def LogInWithEmailAndPassword(email, password):
	try:
		ei = ExternalIdentity.get(email=email)
	except:
		pass
	else:
		if ei.user.check_password(password):
			request.user = user
			Show("You've logged in")
			return

	Show("Bad email/password")

def RegisterWithEmailAndPassword(email, password):
	if not settings.ENABLE_REGISTRATION:
		raise SuspiciousOperation()

	try:
		ei = ExternalIdentity.get(email=email)
	except:
		user = User.create(password=password)
		Send(email, email_confirmation_link(user, email, True))
		# Note: We can't log in here, as we can't log in in the "except" case,
		# and it would tell the attacker if this e-mail is in the database
	else:
		if ei.trusted:
			Send(ei.email, password_change_confirmation_link(user, password))
		else:
			Send(ei.email, "You already have an account; log in with: " + str(user.external_identities) + "or" + ("password" if user.has_password))

	Show("Registered, check e-mail")

def ResetForgottenPassword(email):
	try:
		ei = ExternalIdentity.get(email=email)
	except:
		pass
	else:
		if ei.trusted:
			Send(ei.email, password_reset_link(user))
		else:
			Send(ei.email, "You already have an account; log in with: " + str(ei.user.external_identities) + "or" + ("password" if ei.user.has_password))

	Show("Check e-mail")

def ExternalLogIn(ei: ExternalIdentity):
	if ei.trusted and ei.exists:
		request.user = ei.user
	else:
		existing_ai = [ai for ai in ei.additional_identites if ai.exists]

		if TODO: # This is complicated, will be insecure if configured incorrectly, and I'm not sure if we really need this.
			for ai in existing_ai:
				if ei.provider.trusted_for(ai) # Like Google for @gmail.com
						and ai.trusted:
					ei.user = user
					ei.save()
					request.user = user
					return

		if existing_ai:
			Ask user if he wants to merge accounts (=> log in with another) or create a new one
			# Note: In this case we can expose the fact that we have
			# this EI in the database, as the user has shown
			# quite a strong relationship with this EI.
			return

		if not ei.provider.allow_registration:
			raise SuspiciousOperation()

		ei.user = User.create()
		ei.save()
		request.user = ei.user

		Optionally ask user about trusting ei.additional_identites.

def ConfirmEmail(user, email, trusted): # assumes that link authenticity was checked before
	ei = ExternalIdentity.create(email=email, user=user, trusted=trusted)

	if ei.trusted:
		request.user = user # Because he can reset password and then log in anyway
