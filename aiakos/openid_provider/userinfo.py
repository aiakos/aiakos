from .scopes import SCOPES


def makeUserInfo(user, client, scope):
	data = {}

	for s in scope:
		if s == 'openid':
			data.update({
				'sub': str(user.id), # TODO pairwise subs
			})

		else:
			data.update(SCOPES[s](user).claims)

	return data
