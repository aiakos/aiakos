from ._oauth2 import OAuth2Client
from ._util import clean
import requests

class Client(OAuth2Client):
	def get_configuration(self):
		# Check if the URL is correct
		requests.get(self.url).raise_for_status()
		return {
			"issuer": self.url,
			"authorization_endpoint": self.url + "oauth/authorize",
			"token_endpoint": self.url + "oauth/token",
			"userinfo_endpoint": self.url + "api/v3/user",
			"response_types_supported": ["code"],
			"subject_types_supported": ["public"],
			"token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"]
		}

	def translate_scope_in(self, scope):
		for scope_token in scope:
			if scope_token in ["openid", "profile", "email", "phone", "address"]:
				yield "read_user"
			else:
				yield scope_token

	def translate_scope_out(self, scope):
		for scope_token in scope:
			if scope_token == "read_user":
				yield "openid"
				yield "profile"
				yield "email"
				# GitLab does not support phone at all.
				yield "address"
			else:
				yield scope_token

	def translate_userinfo(self, userinfo):
		if userinfo["state"] != "active":
			return None

		return clean({
			"sub": userinfo.get("id"),
			"name": userinfo.get("name"),
			"nickname": userinfo.get("username"),
			"profile": userinfo.get("web_url"),
			"picture": userinfo.get("avatar_url"),
			"website": userinfo.get("website_url"),
			"email": userinfo.get("email"),
			"email_verified": True if userinfo.get("confirmed_at") else False,
			"address": {
				"formatted": userinfo.get("location"),
			},

			"openid-connect-python/bio": userinfo.get("bio"),
			"openid-connect-python/created_at": userinfo.get("created_at"),
			"openid-connect-python/is_admin": userinfo.get("is_admin"),
			"openid-connect-python/two_factor_enabled": userinfo.get("two_factor_enabled"),
			"openid-connect-python/organization": userinfo.get("organization"),

			"openid-connect-python/gitlab": {
				"can_create_group": userinfo.get("can_create_group"),
				"can_create_project": userinfo.get("can_create_project"),
				"color_scheme_id": userinfo.get("color_scheme_id"),
				"projects_limit": userinfo.get("projects_limit"),
				"theme_id": userinfo.get("theme_id"),
			}
		})

		"""
		TODO map:

		external: false
		identities:
		- extern_uid: '9737'
		provider: github
		linkedin: ''
		skype: ''
		twitter: ''
		"""
