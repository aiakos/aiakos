import os

from django.core.management.base import BaseCommand

from Cryptodome.PublicKey import RSA

from ...models import RSAKey


class Command(BaseCommand):
	help = "Randomly generate a new RSA key for the OpenID Provider"

	def handle(self, *args, **options):
		try:
			key = RSA.generate(1024)
			rsakey = RSAKey(key=key.exportKey('PEM').decode('utf8'))
			rsakey.save()
			self.stdout.write("RSA key successfully created with kid: {0}".format(rsakey.kid))
		except Exception as e:
			self.stdout.write("Something goes wrong: {0}".format(e))