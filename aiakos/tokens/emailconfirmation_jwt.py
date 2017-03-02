import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from jose import JOSEError, jwt

User = get_user_model()
logger = logging.getLogger(__name__)

def makeEmailConfirmationToken(user, email):
	return jwt.encode({
		'user': str(user.id),
		'email': email,
		'exp': int((timezone.now() + timedelta(days=3)).timestamp()),
		'aiakosauth.com/use': 'aiakos.emailconfirmation',
	}, settings.SECRET_KEY, algorithm='HS256')

class EmailConfirmationToken:
	pass

def expandEmailConfirmationToken(token):
	try:
		data = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
		if data['aiakosauth.com/use'] != 'aiakos.emailconfirmation':
			return None

		ret = EmailConfirmationToken()
		ret.user = User.objects.get(id=data['user'])
		ret.email = data['email']
		return ret
	except (JOSEError, KeyError):
		return None
	except:
		logger.exception("Cannot decode email confirmation token.")
		return None
