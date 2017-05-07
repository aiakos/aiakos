from django.http import HttpResponse


def check_health(request):
	# TODO Check if database is OK.
	return HttpResponse("OK")

def HealthcheckMiddleware(get_response):
	"""
	Responds 200 on /.health.

	This cannot be done using a Django view, because:
	- health checkers use invalid hostname
	- SECURE_SSL_REDIRECT makes Django respond with 301 before the view gets called

	On the other side, this means that we don't really test if the service is 100% healthy...
	"""

	def handle_healthcheck(request):
		if request.path == "/.health":
			return check_health(request)

		return get_response(request)

	return handle_healthcheck
