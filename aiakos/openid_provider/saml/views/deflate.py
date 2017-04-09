import zlib


def deflate(value):
	return zlib.compress(value)[2:-4]

def inflate(value):
	return zlib.decompress(value, -15)
