from .auth_request import AuthRequest


class FlowMixin:
	class Fields:
		auth_request = AuthRequest
