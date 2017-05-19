import json
import logging
from urllib.parse import urlencode, urlsplit, urlunsplit
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt, csrf_protect, requires_csrf_token
from django.views.generic import View

from ..errors import *
from ..models import Client, UserConsent
from ..scopes import SCOPES
from ..tokens import *

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class AuthorizationView(View):

	def _authorize(self, params):
		try:
			_state_id = self.request.POST['_state']
		except:
			try:
				_state_id = self.request.GET['_state']
			except:
				_state_id = None

		if _state_id:
			try:
				params = json.loads(self.request.COOKIES['auth_state_' + _state_id])
			except Exception as e:
				logger.warning(e)
				pass

		try:
			response_type = set(params['response_type'].split(' '))
			client_id = params['client_id']
			redirect_uri = params['redirect_uri']
		except KeyError:
			return HttpResponseBadRequest()

		try:
			User = get_user_model()
			service_account = User.objects.get(id=client_id)
		except User.DoesNotExist:
			return HttpResponseNotFound(_("Invalid client ID"))

		try:
			client = service_account.openid_client
		except Client.DoesNotExist:
			return HttpResponseNotFound(_("Invalid client ID"))

		if not client.is_valid_redirect_uri(redirect_uri):
			return HttpResponseNotFound(_("Invalid redirect URI"))

		state = params.get('state', '')

		try:
			try:
				response_mode = params.get('response_mode', 'query' if response_type == {'code'} else 'fragment')
				if response_mode != 'fragment' and " ".join(response_type) not in {'code', 'token'}:
					response_mode = 'fragment'
					raise invalid_request()

				scope = set(params.get('scope', '').split(' '))
				scope &= set(['openid']) | set(SCOPES.keys())

				untrusted_scope = scope - client.trusted_scopes

				if '_cf' in self.request.POST:
					consent = self._handle_consent_form(self.request, client, untrusted_scope)
				else:
					consent = None

				nonce = params.get('nonce', '')
				if response_type != {'code'} and nonce == '':
					raise invalid_request()

				display = params.get('display', '')
				prompt = params.get('prompt', '')
				max_age = params.get('max_age', '')
				ui_locales = params.get('ui_locales', '')
				id_token_hint = params.get('id_token_hint', '')
				login_hint = params.get('login_hint', '') # We don't need this, we have a session.
				acr_values = params.get('acr_values', '')
				claims_locales = params.get('claims_locales', '')
				claims = params.get('claims', '')

				request = params.get('request', '')
				request_uri = params.get('request_uri', '')

				if request:
					raise request_not_supported()
				
				if request_uri:
					raise request_uri_not_supported()

				requested_sub = ''

				if id_token_hint:
					# TODO decode without checking signature, right? we might have rotated these keys out already
					#requested_sub = id_hint['sub']
					pass
		
				if claims:
					# TODO OPTIONAL
					# - set requested_sub
					pass

				if requested_sub:
					if str(self.request.user.id) != requested_sub:
						raise login_required()

				if prompt == 'login':
					raise login_required()
				elif prompt == 'select_account':
					raise account_selection_required()

				if not self.request.user.is_authenticated:
					raise login_required()

				if False: # TODO There is no self.request.session['auth_time'].
					if max_age:
						if int(self.request.session['auth_time']) + int(max_age) > time():
							raise login_required()

				if consent:
					scope &= (consent.scope | client.trusted_scopes)
				else:
					if prompt == 'consent':
						raise consent_required()

					if untrusted_scope:
						try:
							uc = UserConsent.objects.get(user=self.request.user, client=client)
							if not untrusted_scope.issubset(uc.scope):
								raise consent_required()
						except UserConsent.DoesNotExist:
							raise consent_required()

				response = {}

				if state:
					response['state'] = state

				if 'code' in response_type:
					code = makeCode(client=client, user=self.request.user, scope=scope, nonce=nonce)
					response['code'] = code
				else:
					code = None

				if 'token' in response_type:
					token_type, access_token, expires_in = makeAccessToken(client=client, user=self.request.user, scope=scope, confidential=False)
					response['token_type'] = token_type
					response['access_token'] = access_token
					response['expires_in'] = expires_in
				else:
					access_token = None

				if 'id_token' in response_type and 'openid' in scope:
					id_token = makeIDToken(request=self.request, client=client, user=self.request.user, scope=scope, nonce=nonce, at=access_token, c=code)
					response['id_token'] = id_token
				else:
					id_token = None

				return self._redirect(redirect_uri, response_mode, response)

			except login_required:
				if prompt == 'none':
					raise interaction_required() # Note: we don't want to tell RP if the user is logged in or not

				if "error" in self.request.GET: # User cancelled log in.
					raise access_denied()

				params = {k: v for k, v in params.items() if k != 'prompt'}
				_state = json.dumps(params)
				_state_id = uuid4().hex
				res = redirect_to_login(self.request.path + '?_state=' + _state_id)
				res.set_cookie('auth_state_' + _state_id, _state)
				return res

			except consent_required:
				if prompt == 'none':
					raise interaction_required() # Note: we don't want to tell RP if the user is logged in or not

				params = {k: v for k, v in params.items() if k != 'prompt'}
				_state = json.dumps(params)
				_state_id = uuid4().hex
				res = self._render_consent_form(self.request, client, untrusted_scope, _state_id)
				res.set_cookie('auth_state_' + _state_id, _state)
				return res

			except account_selection_required:
				if prompt == 'none':
					raise interaction_required() # Note: we don't want to tell RP if the user is logged in or not

				params = {k: v for k, v in params.items() if k != 'prompt'}
				raise # TODO MAYBE SOMEDAY

		except OAuthError as e:
			logger.debug("OAuth error", exc_info=True)
			response = {
				'error': type(e).__name__,
				'error_description': e.description,
			}
			if state:
				response['state'] = state
			return self._redirect(redirect_uri, response_mode, response)

		except Exception as e:
			logger.error('Internal error', exc_info=True)
			response = {
				'error': 'server_error',
				'error_description': 'Internal Server Error',
			}
			if state:
				response['state'] = state
			return self._redirect(redirect_uri, response_mode, response)

	@staticmethod
	def _redirect(redirect_uri, response_mode, response):
		redirect_uri = urlsplit(redirect_uri)

		if response_mode == 'query':
			new_query = redirect_uri.query
			if new_query:
				new_query += '&'
			new_query += urlencode(response)
			redirect_uri = redirect_uri._replace(query=new_query)

		elif response_mode == 'fragment':
			new_fragment = redirect_uri.fragment
			if new_fragment:
				new_fragment += '&'
			new_fragment += urlencode(response)
			redirect_uri = redirect_uri._replace(fragment=new_fragment)

		return redirect(urlunsplit(redirect_uri))

	@staticmethod
	@requires_csrf_token
	def _render_consent_form(request, client, scope, state):
		context = {
			'client': client,
			'scope': {name: desc for name, desc in SCOPES.items() if name in scope},
			'hidden_inputs': mark_safe('<input type="hidden" name="_cf" value="1"><input type="hidden" name="_state" value="{}">'.format(state)),
		}

		return render(request, 'openid_provider/authorize.html', context)

	@staticmethod
	@csrf_protect
	def _handle_consent_form(request, client, scope):
		if '_allow' not in request.POST:
			raise access_denied()

		if client.confidential:
			uc, created = UserConsent.objects.get_or_create(user=request.user, client=client)
		else:
			uc = UserConsent(user=request.user, client=client)

		uc.scope |= scope # TODO add a way to turn on and off single permissions

		if client.confidential:
			uc.save()

		return uc

	def get(self, request):
		self.request = request
		return self._authorize(request.GET)

	def post(self, request):
		self.request = request
		return self._authorize(request.POST)
