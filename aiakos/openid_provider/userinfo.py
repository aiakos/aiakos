
def makeUserInfo(user, client, scope):
	data = {
		'sub': str(user.id), # TODO pairwise subs
	}

	# TODO add userdata claims

	return data
