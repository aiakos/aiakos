from django.conf import settings
from django.shortcuts import redirect


def prepend_user(request):
	if request.user.default:
		return redirect('/u/{}{}'.format(str(request.user.default.id), request.get_full_path()))

	return redirect(settings.LOGIN_URL)
