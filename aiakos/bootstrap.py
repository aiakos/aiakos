import os

DEFAULT_THEME_URL = "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css"
DEFAULT_THEME_INTEGRITY = "sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp"

class Theme:
	def __init__(self, url, integrity=None):
		self.url = url
		self.integrity = integrity

def theme(request):
	theme = Theme(
		os.environ.get("BOOTSTRAP_THEME_URL", DEFAULT_THEME_URL),
		os.environ.get("BOOTSTRAP_THEME_INTEGRITY"),
	)
	
	if theme.integrity is None:
		theme.integrity = DEFAULT_THEME_INTEGRITY if theme.url == DEFAULT_THEME_URL else ""

	return {
		'bootstrap_theme': theme
	}
