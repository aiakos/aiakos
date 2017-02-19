
def clean(d):
	if isinstance(d, dict):
		return {k: clean(v) for k, v in d.items() if v is not None}
	elif isinstance(d, list):
		return [clean(v) for v in d if v is not None]
	else:
		return d
