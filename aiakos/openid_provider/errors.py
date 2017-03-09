
class OAuthError(Exception):
	def __init__(self, description=None):
		if description:
			self.description = description

class invalid_request(OAuthError):
	description = """The request is missing a required parameter, includes an invalid parameter value, repeats the same parameter, or is otherwise malformed."""
	status_code = 400

class unauthorized_client(OAuthError):
	description = """The client is not authorized to make this request."""
	status_code = 403

class access_denied(OAuthError):
	description = """The resource owner or authorization server denied the request."""
	status_code = 403

class unsupported_response_type(OAuthError):
	description = """The authorization server does not support obtaining an authorization code using this method."""
	status_code = 501

class invalid_scope(OAuthError):
	description = """The requested scope is invalid, unknown, or malformed."""
	status_code = 400

class server_error(OAuthError):
	description = """The authorization server encountered an unexpected condition that prevented it from fulfilling the request."""
	status_code = 500

class temporarily_unavailable(OAuthError):
	description = """The authorization server is currently unable to handle the request due to a temporary overloading or maintenance of the server."""
	status_code = 503

class invalid_client(OAuthError):
	description = """Client authentication failed (e.g., unknown client, no client authentication included, or unsupported authentication method). """
	status_code = 401

class invalid_grant(OAuthError):
	description = """The provided authorization grant (e.g., authorization code, resource owner credentials) or refresh token is invalid, expired, revoked, does not match the redirection URI used in the authorization request, or was issued to another client."""
	status_code = 401

class unsupported_grant_type(OAuthError):
	description = """The authorization grant type is not supported by the authorization server."""
	status_code = 501

class invalid_token(OAuthError):
	description = """The access token provided is expired, revoked, malformed, or invalid for other reasons."""
	status_code = 401

class insufficient_scope(OAuthError):
	description = """The request requires higher privileges than provided by the access token."""
	status_code = 403

class unsupported_token_type(OAuthError):
	description = """The authorization server does not support the revocation of the presented token type."""
	status_code = 501

class interaction_required(OAuthError):
	description = """The Authorization Server requires End-User interaction of some form to proceed."""

class login_required(OAuthError):
	description = """The Authorization Server requires End-User authentication."""

class account_selection_required(OAuthError):
	description = """The End-User is REQUIRED to select a session at the Authorization Server."""

class consent_required(OAuthError):
	description = """The Authorization Server requires End-User consent."""

class invalid_request_uri(OAuthError):
	description = """The request_uri in the Authorization Request returns an error or contains invalid data."""

class invalid_request_object(OAuthError):
	description = """The request parameter contains an invalid Request Object."""

class request_not_supported(OAuthError):
	description = """The OP does not support use of the request parameter."""

class request_uri_not_supported(OAuthError):
	description = """The OP does not support use of the request_uri parameter."""

class registration_not_supported(OAuthError):
	description = """The OP does not support use of the registration parameter."""
