from django.conf import settings
from django.db import models

class Profile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)

	name = models.CharField(max_length=200, blank=True)
	given_name = models.CharField(max_length=200, blank=True)
	family_name = models.CharField(max_length=200, blank=True)
	middle_name = models.CharField(max_length=200, blank=True)
	nickname = models.CharField(max_length=200, blank=True)
	preferred_username = models.CharField(max_length=200, blank=True)
	profile = models.URLField(max_length=200, blank=True)
	picture = models.URLField(max_length=200, blank=True)
	website = models.URLField(max_length=200, blank=True)
	gender = models.CharField(max_length=200, blank=True)
	birthdate = models.DateField(null=True, blank=True)
	zoneinfo = models.CharField(max_length=200, blank=True)
	locale = models.CharField(max_length=200, blank=True)

	email = models.EmailField(blank=True)
	email_verified = models.BooleanField(default=False)

	phone_number = models.CharField(max_length=15, blank=True)
	phone_number_verified = models.BooleanField(default=False)

	address_formatted = models.TextField(blank=True)
	address_street = models.TextField(blank=True)
	address_locality = models.TextField(blank=True)
	address_region = models.TextField(blank=True)
	address_postal_code = models.TextField(blank=True)
	address_country = models.TextField(blank=True)

	@property
	def address(self):
		return {
			"formatted": self.address_formatted,
			"street_address": self.address_street,
			"locality": self.address_locality,
			"region": self.address_region,
			"postal_code": self.address_postal_code,
			"country": self.address_country,
		}

	@address.setter
	def address(self, v):
		self.address_formatted = v.get("formatted", "")
		self.address_street = v.get("street_address", "")
		self.address_locality = v.get("locality", "")
		self.address_region = v.get("region", "")
		self.address_postal_code = v.get("postal_code", "")
		self.address_country = v.get("country", "")

	def __str__(self):
		return str(self.user)

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)

		self.user.email = self.email if self.email_verified else ""
		self.user.first_name = self.given_name
		self.user.last_name = self.family_name
		self.user.save()

	def from_dict(d):
		p = Profile()

		for field in Profile._meta.get_fields():
			if field.name not in ['id', 'user'] and not field.name.startswith("address_"):
				v = d.get(field.name)
				if v is not None:
					setattr(p, field.name, v)

		p.address = d.get("address", {})

		return p

	def fill_missing(self, other):
		for field in Profile._meta.get_fields():
			if field.name not in ['id', 'user', 'email', 'email_verified', 'phone_number', 'phone_number_verified']:
				if not getattr(self, field.name):
					setattr(self, field.name, getattr(other, field.name))

		if not self.email:
			self.email = other.email
			self.email_verified = other.email_verified
		elif not self.email_verified and other.email_verified:
			self.email = other.email
			self.email_verified = other.email_verified

		if not self.phone_number:
			self.phone_number = other.phone_number
			self.phone_number_verified = other.phone_number_verified
		elif not self.phone_number_verified and other.phone_number_verified:
			self.phone_number = other.phone_number
			self.phone_number_verified = other.phone_number_verified
