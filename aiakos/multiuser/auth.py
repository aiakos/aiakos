from functools import partial

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in

SESSION_ACCOUNTS = '_auth_accounts'
SESSION_DEFAULT_ACCOUNT = '_auth_default_account'

Account = get_user_model()


class User:
	def __init__(self, request):
		self.request = request

	@property
	def accounts(self):
		try:
			return self._accounts
		except AttributeError:
			try:
				account_ids = set(self.request.session[SESSION_ACCOUNTS])
			except KeyError:
				account_ids = set()
			self._accounts = set(acc for acc in [Account.objects.get(pk=user_id) for user_id in account_ids] if acc.is_active)

			if self.request.path.startswith('/u/'):
				for acc in self._accounts:
					acc.switch = partial(switch_account, self.request, acc)

			return self._accounts

	@accounts.setter
	def accounts(self, accounts):
		self._accounts = accounts
		self.request.session[SESSION_ACCOUNTS] = [str(acc.id) for acc in self.accounts]

	@property
	def default(self):
		try:
			return self._default
		except AttributeError:
			try:
				self._default = next(iter(self.accounts))
			except StopIteration:
				self._default = None
			try:
				default_id = self.request.session[SESSION_DEFAULT_ACCOUNT]
			except KeyError:
				self._default = None
			else:
				for acc in self.accounts:
					if str(acc.id) == default_id:
						self._default = acc
			return self._default

	@default.setter
	def default(self, account):
		self._default = account
		self.request.session[SESSION_DEFAULT_ACCOUNT] = str(account.id)

	@property
	def is_authenticated(self):
		return bool(self.accounts)

	@property
	def is_anonymous(self):
		return not self.is_authenticated

	def login(self, account):
		self.accounts = self.accounts | {account}
		self.default = account
		user_logged_in.send(sender=account.__class__, request=self.request, user=account)

	def has_perm(self, perm, obj=None):
		# TODO Make it possible to create user permissions that are not auto-granted to users.
		if obj in self.accounts:
			return True

		for acc in self.accounts:
			if acc.has_perm(perm, obj):
				return True

		return False

	def has_perms(self, perm_list, obj=None):
		return all(self.has_perm(perm, obj) for perm in perm_list)

	def has_module_perms(self, app_label):
		for acc in self.accounts:
			if acc.has_module_perms(app_label):
				return True

		return False

	# For admin site:

	@property
	def is_active(self):
		return self.is_authenticated

	@property
	def is_staff(self):
		return any(acc.is_staff for acc in self.accounts)

	@property
	def pk(self):
		return self.default.pk

	def get_username(self):
		return self.default.get_username()


def get_user(request):
	return User(request)


def login(request, account):
	request.user.login(account)


def switch_account(request, account):
	nothing, u, old, path = request.path.split('/', 3)
	return '/u/{}/{}'.format(account.id, path)
