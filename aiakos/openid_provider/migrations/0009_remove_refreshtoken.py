# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-31 17:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

	dependencies = [
		('openid_provider', '0008_remove_accesstoken'),
	]

	operations = [
		migrations.RemoveField(
			model_name='refreshtoken',
			name='client',
		),
		migrations.RemoveField(
			model_name='refreshtoken',
			name='user',
		),
		migrations.DeleteModel(
			name='RefreshToken',
		),
	]
