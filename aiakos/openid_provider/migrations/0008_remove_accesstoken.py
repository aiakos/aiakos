# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-21 18:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

	dependencies = [
		('openid_provider', '0007_client'),
	]

	operations = [
		migrations.RemoveField(
			model_name='accesstoken',
			name='client',
		),
		migrations.RemoveField(
			model_name='accesstoken',
			name='user',
		),
		migrations.DeleteModel(
			name='AccessToken',
		),
	]
