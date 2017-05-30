import sys

from .uri_list import URIList, uri_matches

tests = [
	(('https://lorem.ipsum.tld/a', ['https://lorem.ipsum.tld/a'], False), True),
	(('https://lorem.ipsum.tld/b', ['https://lorem.ipsum.tld/a'], False), False),
	(('https://lorem.ipsum.tld/a', ['https://*.ipsum.tld/a'], False), False),
	(('https://lorem.ipsum.tld/a', ['https://*.ipsum.tld/a'], True), True),
	(('https://lorem.ipsum.tld/b', ['https://*.ipsum.tld/a'], True), False),
	(('https://lo.em.ipsum.tld/a', ['https://*.ipsum.tld/a'], True), False),
]

ret = 0

for input, output in tests:
	if not uri_matches(*input) == output:
		print("ERROR: uri_matches{} returned: {}".format(input, uri_matches(*input)), file=sys.stderr)
		ret = 1

for input, output in tests:
	if not (input[0] in URIList(*input[1:])) == output:
		print("ERROR: {} in URIList{} returned: {}".format(input[0], input[1:], uri_matches(*input)), file=sys.stderr)
		ret = 1

sys.exit(ret)
