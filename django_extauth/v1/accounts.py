from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.http import Http404
from django.utils.crypto import get_random_string

from rest_framework import filters, serializers, viewsets

Account = get_user_model()


class AccountSerializer(serializers.Serializer):
	uri = serializers.HyperlinkedIdentityField(read_only = True, view_name = 'account-detail')
	id = serializers.UUIDField(read_only = True)

	username = serializers.CharField()

	password = serializers.CharField(write_only = True, required = False)
	hashed_password = serializers.CharField(write_only = True, required = False)

	given_name = serializers.CharField(allow_blank = True, required = False)
	middle_name = serializers.CharField(allow_blank = True, required = False)
	family_name = serializers.CharField(allow_blank = True, required = False)

	name = serializers.CharField(read_only = True)
	nickname = serializers.CharField(read_only = True)

	date_joined = serializers.DateTimeField(required = False)
	last_login = serializers.DateTimeField(allow_null = True, required = False)

	emails = serializers.ListSerializer(child = serializers.CharField())

	# DRF hack - because list fields aren't displayed in forms
	email = serializers.CharField(required = False)

	self_writable = {'given_name', 'middle_name', 'family_name', 'password'}
	admin_writable = self_writable | {'username', 'hashed_password', 'date_joined', 'last_login', 'emails', 'email'}

	def validate(self, data):
		all_writable = [f.field_name for f in self._writable_fields]

		writable = set()
		request_user = self.context['request'].user
		if (hasattr(request_user, 'accounts') and self.instance in request_user.accounts) or self.instance == request_user:
				writable |= self.self_writable
		if request_user.has_perm('auth.edit_user'):
			writable |= self.admin_writable

		errors = OrderedDict()
		for field in data.keys():
			if field in all_writable:
				if not field in writable:
					errors[field] = "You are not allowed to change this field."

		if errors:
			raise serializers.ValidationError(errors)

		return data

	def update(self, instance, validated_data):
		if not instance.username:
			instance.username = instance.id
			instance.save()

		for attr, value in validated_data.items():
			if attr == 'password':
				instance.set_password(value)
			elif attr == 'hashed_password':
				instance.password = value
			elif attr == 'email':
				if not 'emails' in validated_data:
					instance.emails = [value]
			else:
				setattr(instance, attr, value)

		instance.save()
		return instance


class AdminAccountSerializer(AccountSerializer):
	date_joined = serializers.DateTimeField(required = False)
	last_login = serializers.DateTimeField(required = False)


class OnlySelfAndOwnedFilter(filters.BaseFilterBackend):
	def filter_queryset(self, request, queryset, view):
		if hasattr(request.user, 'accounts'):
			pks = [a.pk for a in request.user.accounts]
		else:
			pks = [request.user.pk]

		return queryset.filter(Q(pk__in=pks) | Q(oauth_app__owner__pk__in=pks))


class AccountViewSet(viewsets.ModelViewSet):
	queryset = Account.objects.all()
	filter_backends = (OnlySelfAndOwnedFilter,)
	serializer_class = AccountSerializer

	def filter_queryset(self, queryset):
		if not self.request.user.has_perm('auth.edit_user') or self.action == 'list':
			return super().filter_queryset(queryset)
		return queryset

	def get_object(self):
		try:
			return super().get_object()
		except Http404:
			if self.request.user.has_perm('auth.edit_user') and self.action != 'retrieve':
				return Account(id=self.kwargs['pk'])
			raise
