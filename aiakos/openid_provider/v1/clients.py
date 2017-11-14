from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils.crypto import get_random_string

from rest_framework import filters, serializers, viewsets

from ..models import App

Account = get_user_model()


class ClientManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().exclude(oauth_app=None)

	def create(self, owner=None, **kwargs):
		c = Client(oauth_app=App(), **kwargs)

		if owner:
			c.oauth_app.owner_id = owner.pk

			if owner.oauth_app:
				c.oauth_app.trusted_scopes = owner.oauth_app.trusted_scopes & getattr(c.oauth_app, 'new_trusted_scope', set())

		if c.oauth_auth_method.startswith('client_secret_'):
			c.client_secret = get_random_string(32)
			c.set_password(c.client_secret)

		c.username = str(c.id)

		c.save()
		return c


class Client(Account):
	objects = ClientManager()

	class Meta:
		proxy = True

	@property
	def client_id(self):
		return str(self.id)

	@property
	def client_id_issued_at(self):
		return self.date_joined

	@property
	def client_name(self):
		return self.oauth_app.name

	@client_name.setter
	def client_name(self, val):
		self.oauth_app.name = val

	@property
	def client_uri(self):
		return self.oauth_app.uri

	@client_uri.setter
	def client_uri(self, val):
		self.oauth_app.uri = val

	@property
	def initiate_login_uri(self):
		return self.oauth_app.initiate_login_uri

	@initiate_login_uri.setter
	def initiate_login_uri(self, val):
		self.oauth_app.initiate_login_uri = val

	@property
	def logo_uri(self):
		return self.oauth_app.logo_uri

	@logo_uri.setter
	def logo_uri(self, val):
		self.oauth_app.logo_uri = val

	@property
	def tos_uri(self):
		return self.oauth_app.tos_uri

	@tos_uri.setter
	def tos_uri(self, val):
		self.oauth_app.tos_uri = val

	@property
	def policy_uri(self):
		return self.oauth_app.policy_uri

	@policy_uri.setter
	def policy_uri(self, val):
		self.oauth_app.policy_uri = val

	@property
	def contacts(self):
		return self.oauth_app.contacts

	@contacts.setter
	def contacts(self, val):
		self.oauth_app.contacts = val

	@property
	def redirect_uris(self):
		return self.oauth_redirect_uris

	@redirect_uris.setter
	def redirect_uris(self, val):
		self.oauth_redirect_uris = val

	@property
	def post_logout_redirect_uris(self):
		return self.oauth_post_logout_redirect_uris

	@post_logout_redirect_uris.setter
	def post_logout_redirect_uris(self, val):
		self.oauth_post_logout_redirect_uris = val

	@property
	def application_type(self):
		return self.oauth_application_type

	@application_type.setter
	def application_type(self, val):
		self.oauth_application_type = val

	@property
	def token_endpoint_auth_method(self):
		return self.oauth_auth_method

	@token_endpoint_auth_method.setter
	def token_endpoint_auth_method(self, val):
		self.oauth_auth_method = val

	registration_access_token = None
	client_secret = None

	@property
	def client_secret_expires_at(self):
		if self.oauth_auth_method.startswith('client_secret_'):
			return 0
		else:
			return None

	@property
	def software_id(self):
		return self.oauth_software_id

	@software_id.setter
	def software_id(self, val):
		self.oauth_software_id = val

	@property
	def software_version(self):
		return self.oauth_software_version

	@software_version.setter
	def software_version(self, val):
		self.oauth_software_version = val

	@property
	def trusted_scope(self):
		return self.oauth_app.trusted_scopes

	@trusted_scope.setter
	def trusted_scope(self, val):
		self.oauth_app.new_trusted_scope = set(val)

	def save(self):
		self.oauth_app.trusted_scopes = self.oauth_app.trusted_scopes & getattr(self.oauth_app, 'new_trusted_scope', set())

		self.oauth_app.save()
		self.oauth_app = self.oauth_app
		super().save()

	def delete(self):
		super().delete()
		if self.oauth_app.service_account_set.count() == 0:
			self.oauth_app.delete()

	# DRF hack
	@property
	def redirect_uri(self):
		raise AttributeError()

	@redirect_uri.setter
	def redirect_uri(self, val):
		self.oauth_redirect_uris = [val]

	@property
	def post_logout_redirect_uri(self):
		raise AttributeError()

	@post_logout_redirect_uri.setter
	def post_logout_redirect_uri(self, val):
		self.oauth_post_logout_redirect_uris = [val]


class ClientSerializer(serializers.Serializer):
	registration_client_uri = serializers.HyperlinkedIdentityField(read_only = True, view_name = 'client-detail')
	client_id = serializers.CharField(read_only = True)
	client_id_issued_at = serializers.DateTimeField(read_only = True)
	client_secret = serializers.CharField(read_only = True)
	client_secret_expires_at = serializers.IntegerField(read_only = True)
	client_name = serializers.CharField(required = False, allow_blank = True)
	client_uri = serializers.URLField(required = False, allow_blank = True)
	initiate_login_uri = serializers.URLField(required = False, allow_blank = True)
	logo_uri = serializers.URLField(required = False, allow_blank = True)
	tos_uri = serializers.URLField(required = False, allow_blank = True)
	policy_uri = serializers.URLField(required = False, allow_blank = True)
	contacts = serializers.ListSerializer(child = serializers.CharField(), required = False)
	redirect_uris = serializers.ListSerializer(child = serializers.URLField(), required = False)
	post_logout_redirect_uris = serializers.ListSerializer(child = serializers.URLField(), required = False)
	application_type = serializers.ChoiceField(choices=Client.OAUTH_APPLICATION_TYPES, default = 'web', required = False)
	token_endpoint_auth_method = serializers.ChoiceField(choices=Client.OAUTH_AUTH_METHODS, default = 'client_secret_basic', required = False)
	software_id = serializers.CharField(required = False, allow_blank = True)
	software_version = serializers.CharField(required = False, allow_blank = True)
	trusted_scope = serializers.ListSerializer(child = serializers.CharField(), required = False)

	owner = serializers.CharField(read_only=True)

	# DRF hack - because list fields aren't displayed in forms
	redirect_uri = serializers.URLField(write_only = True, required = False, allow_blank = True)
	post_logout_redirect_uri = serializers.URLField(write_only = True, required = False, allow_blank = True)

	def create(self, validated_data):
		owner = self.context['request'].user
		if not owner.is_authenticated:
			owner = None
		return Client.objects.create(**validated_data, owner = owner)

	def update(self, instance, validated_data):
		for attr, value in validated_data.items():
			setattr(instance, attr, value)

		instance.save()
		return instance


class OnlySelfAndOwnedFilter(filters.BaseFilterBackend):
	def filter_queryset(self, request, queryset, view):
		if hasattr(request.user, 'accounts'):
			pks = [a.pk for a in request.user.accounts]
		else:
			pks = [request.user.pk]

		return queryset.filter(Q(pk__in=pks) | Q(oauth_app__owner__pk__in=pks))


class ClientViewSet(viewsets.ModelViewSet):
	queryset = Client.objects.all()
	filter_backends = (OnlySelfAndOwnedFilter,)
	serializer_class = ClientSerializer

	def filter_queryset(self, queryset):
		if self.action == 'retrieve':
			return queryset
		return super().filter_queryset(queryset)
