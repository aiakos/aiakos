from django.http.request import *

IGNORE_ALLOWED_HOSTS_FOR_UAS = [
	"ELB-HealthChecker/2.0",
]

def get_host(request):
	"""Return the HTTP host using the environment or request headers."""
	host = request._get_raw_host()

	# Allow variants of localhost if ALLOWED_HOSTS is empty and DEBUG=True.
	allowed_hosts = settings.ALLOWED_HOSTS
	if settings.DEBUG and not allowed_hosts:
		allowed_hosts = ['localhost', '127.0.0.1', '[::1]']

	ua = request.META.get('HTTP_USER_AGENT', '')
	domain, port = split_domain_port(host)
	if domain and (validate_host(domain, allowed_hosts) or ua in IGNORE_ALLOWED_HOSTS_FOR_UAS):
		return host
	else:
		msg = "Invalid HTTP_HOST header: %r." % host
		if domain:
			msg += " You may need to add %r to ALLOWED_HOSTS." % domain
		else:
			msg += " The domain name provided is not valid according to RFC 1034/1035."
		raise DisallowedHost(msg)

HttpRequest.get_host = get_host
