import requests
from requests.auth import HTTPBasicAuth


class Backend:
	def __init__(self, url):
		self.url = url

	def check_password(self, user, password):
		res = requests.get(self.url, auth=HTTPBasicAuth(user.username, password))
		try:
			res.raise_for_status()
		except:
			return False
		return True
