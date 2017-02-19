from ._oauth2 import OAuth2Client
from ._util import clean
import requests

class Client(OAuth2Client):
	def __init__(self, url, client_id, client_secret, api_url=None):
		if not api_url:
			api_url = url.replace("://", "://api.")

		self._api_url = api_url
		super().__init__(url, client_id, client_secret)

	def get_configuration(self):
		# Check if the URL is correct
		requests.get(self.url).raise_for_status()
		return {
			"issuer": self.url,
			"authorization_endpoint": self.url + "login/oauth/authorize",
			"token_endpoint": self.url + "login/oauth/access_token",
			"userinfo_endpoint": self._api_url + "user",
			"response_types_supported": ["code"],
			"subject_types_supported": ["public"],
			"token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"]
		}

	def translate_scope_in(self, scope):
		for scope_token in scope:
			if scope_token in ["openid", "profile", "email", "phone", "address"]:
				pass
			else:
				yield scope_token

	def translate_scope_out(self, scope):
		yield "openid"
		yield "profile"
		yield "email"
		# GitHub does not support phone at all.
		yield "address"
		for scope_token in scope:
			yield scope_token

	def translate_userinfo(self, userinfo):
		return clean({
			"sub": userinfo.get("id"),
			"name": userinfo.get("name"),
			"nickname": userinfo.get("login"),
			"profile": userinfo.get("html_url"),
			"picture": userinfo.get("avatar_url"),
			"website": userinfo.get("blog"),
			"email": userinfo.get("email"),
			"email_verified": True,
			"address": {
				"formatted": userinfo.get("location"),
			},
			"updated_at": userinfo.get("updated_at"),

			"openid-connect-python/bio": userinfo.get("bio"),
			"openid-connect-python/created_at": userinfo.get("created_at"),
			"openid-connect-python/is_admin": userinfo.get("site_admin"),
			"openid-connect-python/hireable": userinfo.get("hireable"),
			"openid-connect-python/organization": userinfo.get("company"),

			"openid-connect-python/github": {
				"events_url": userinfo.get("events_url"),
				"followers": userinfo.get("followers"),
				"followers_url": userinfo.get("followers_url"),
				"following": userinfo.get("following"),
				"following_url": userinfo.get("following_url"),
				"gists_url": userinfo.get("gists_url"),
				"organizations_url": userinfo.get("organizations_url"),
				"public_gists": userinfo.get("public_gists"),
				"public_repos": userinfo.get("public_repos"),
				"received_events_url": userinfo.get("received_events_url"),
				"repos_url": userinfo.get("repos_url"),
				"starred_url": userinfo.get("starred_url"),
				"subscriptions_url": userinfo.get("subscriptions_url"),
				"url": userinfo.get("url"),
			}
		})

		""" TODO map:

		type: User
		"""
