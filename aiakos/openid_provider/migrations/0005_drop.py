# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-18 16:40
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
		('openid_provider', '0004_auto_20170530_2001'),
	]

	operations = [
		migrations.DeleteModel(
			name='AccessToken',
		),
		migrations.DeleteModel(
			name='Code',
		),
		migrations.DeleteModel(
			name='RefreshToken',
		),
		migrations.DeleteModel(
			name='UserConsent',
		),
		migrations.DeleteModel(
			name='Client',
		),
	]
