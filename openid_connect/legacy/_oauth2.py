from .. import OpenIDClient

class OAuth2Client(OpenIDClient):
	def get_id(self, token_response):
		token_response._userinfo = self.get_userinfo(token_response.access_token)
		return {
			"iss": self.issuer,
			**token_response.userinfo,
		}
