import ssl
from urllib.parse import urlsplit


def hostname_matches(hostname, pattern):
	try:
		ssl.match_hostname({'subject': ((('commonName', pattern),),)}, hostname)
		return True
	except:
		return False

def uri_matches(uri, patterns, allow_wildcard=False):
	if uri in patterns:
		return True

	if allow_wildcard:
		split_uri = urlsplit(uri)

		for pattern in patterns:
			split_pattern = urlsplit(pattern)

			if not hostname_matches(split_uri.hostname, split_pattern.hostname):
				continue

			allowed_uri = pattern.replace(split_pattern.hostname, split_uri.hostname)

			if uri == allowed_uri:
				return True

	return False

class URIList:
	def __init__(self, patterns, allow_wildcard=False):
		self.patterns = patterns
		self.allow_wildcard = allow_wildcard

	def __contains__(self, uri):
		return uri_matches(uri, self.patterns, allow_wildcard=self.allow_wildcard)

	def __iter__(self):
		return iter(self.patterns)
