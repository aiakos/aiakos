import requests
from requests.auth import HTTPBasicAuth
from jose import jwt
from urllib.parse import urlencode

class TokenResponse:
	def __init__(self, data, client=None):
		self._data = data
		self._client = client

	@property
	def access_token(self):
		return self._data["access_token"]

	@property
	def id_token(self):
		return self._data["id_token"]

	@property
	def userinfo(self):
		try:
			return self._userinfo
		except AttributeError:
			userinfo = self._client.get_userinfo(self.access_token)
			if self.id["sub"] != userinfo["sub"]:
				return None
			self._userinfo = userinfo
			return self._userinfo

class OpenIDClient:
	def __init__(self, url, client_id, client_secret):
		self.url = url
		self.client_id = client_id
		self.client_secret = client_secret

		self._configuration = self.get_configuration()

	def get_configuration(self):
		r = requests.get(self.url + ".well-known/openid-configuration")
		r.raise_for_status()
		return r.json()

	def translate_scope_in(self, scope):
		return scope

	def translate_scope_out(self, scope):
		return scope

	def translate_userinfo(self, userinfo):
		return userinfo

	def get_id(self, token_response):
		return jwt.decode(
			token_response.id_token,
			self.keys,
			algorithms = ['RS256'],
			audience = self.client_id,
			issuer = self.issuer,
			access_token = token_response.access_token,
		)

	@property
	def issuer(self):
		return self._configuration["issuer"]

	@property
	def authorization_endpoint(self):
		return self._configuration["authorization_endpoint"]

	@property
	def token_endpoint(self):
		return self._configuration["token_endpoint"]

	@property
	def jwks_uri(self):
		return self._configuration["jwks_uri"]

	@property
	def userinfo_endpoint(self):
		return self._configuration["userinfo_endpoint"]

	@property
	def keys(self):
		r = requests.get(self._configuration["jwks_uri"])
		r.raise_for_status()
		return r.content

	def get_userinfo(self, access_token):
		r = requests.get(self.userinfo_endpoint, headers=dict(
			Authorization = "Bearer " + access_token,
		))
		r.raise_for_status()
		data = r.json()
		return self.translate_userinfo(data)

	def authorize(self, redirect_uri, state, scope=["openid"]):
		scope = set(self.translate_scope_in(scope))
		return self.authorization_endpoint + "?" + urlencode(dict(
			client_id=self.client_id,
			response_type="code",
			redirect_uri=redirect_uri,
			state=state,
			scope=" ".join(scope),
		))

	def request_token(self, redirect_uri, code):
		client_auth = HTTPBasicAuth(self.client_id, self.client_secret)
		r = requests.post(self.token_endpoint, auth=client_auth, data=dict(
			grant_type="authorization_code",
			redirect_uri=redirect_uri,
			code=code,
		), headers={'Accept': 'application/json'})
		r.raise_for_status()
		resp = TokenResponse(r.json(), self)

		if "scope" in resp._data:
			resp.scope = set(self.translate_scope_out(set(resp._data["scope"].split(" "))))
		if not hasattr(resp, "scope") or "openid" in resp.scope:
			resp.id = self.get_id(resp)

		return resp
