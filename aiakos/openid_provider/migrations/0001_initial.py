# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-27 17:45
from __future__ import unicode_literals

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

	initial = True

	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='AccessToken',
			fields=[
				('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
				('expires_at', models.DateTimeField()),
				('_scope', models.TextField(default='')),
				('confidential', models.BooleanField()),
			],
			options={
				'abstract': False,
			},
		),
		migrations.CreateModel(
			name='Client',
			fields=[
				('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('confidential', models.BooleanField(default=True, verbose_name='confidential')),
				('_redirect_uris', models.TextField(default='', help_text='Enter each URI on a new line.', verbose_name='redirect URIs')),
				('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='openid_client', to=settings.AUTH_USER_MODEL, verbose_name='service account')),
			],
			options={
				'verbose_name': 'client',
				'verbose_name_plural': 'clients',
			},
		),
		migrations.CreateModel(
			name='Code',
			fields=[
				('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
				('expires_at', models.DateTimeField()),
				('_scope', models.TextField(default='')),
				('nonce', models.CharField(blank=True, default='', max_length=255)),
				('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='openid_provider.Client')),
				('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
			],
			options={
				'abstract': False,
			},
		),
		migrations.CreateModel(
			name='RefreshToken',
			fields=[
				('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
				('expires_at', models.DateTimeField()),
				('_scope', models.TextField(default='')),
				('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='openid_provider.Client')),
				('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
			],
			options={
				'abstract': False,
			},
		),
		migrations.CreateModel(
			name='RSAKey',
			fields=[
				('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('key', models.TextField(help_text='Paste your private RSA Key here.', verbose_name='key')),
			],
			options={
				'verbose_name': 'RSA key',
				'verbose_name_plural': 'RSA keys',
			},
		),
		migrations.CreateModel(
			name='UserConsent',
			fields=[
				('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('_scope', models.TextField(default='', verbose_name='scopes')),
				('date_given', models.DateTimeField(auto_now_add=True, verbose_name='date given')),
				('date_updated', models.DateTimeField(auto_now=True, verbose_name='date updated')),
				('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='openid_provider.Client', verbose_name='client')),
				('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
			],
			options={
				'verbose_name': 'user consent',
				'verbose_name_plural': 'user consents',
			},
		),
		migrations.AddField(
			model_name='accesstoken',
			name='client',
			field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='openid_provider.Client'),
		),
		migrations.AddField(
			model_name='accesstoken',
			name='user',
			field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
		),
		migrations.AlterUniqueTogether(
			name='userconsent',
			unique_together=set([('user', 'client')]),
		),
	]
