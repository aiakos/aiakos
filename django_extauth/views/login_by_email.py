from django.utils.decorators import method_decorator

from ..token import in_url_authentication
from .auth import AuthView


@method_decorator(in_url_authentication, name='dispatch')
class LoginByEmail(AuthView):
	redirect_authenticated_user = True
