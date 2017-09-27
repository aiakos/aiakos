import os
from urllib.parse import urlsplit

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Application definition

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'raven.contrib.django.raven_compat',
	'crispy_forms',
	'django_inlinecss',
	'rest_framework',

	'aiakos.multiuser',
	'django_request_user',
	'django_extauth',
	'django_passwords',
	'aiakos.openid_provider',
	'aiakos',
]

AUTH_USER_MODEL = 'aiakos.User'

USER_CORE_MODULES = [
	'django_modular_user.user:AbstractBaseUser',
	'django_modular_user.user:UsernameMixin',
	'django_modular_user.user:NamePartsMixin',
	'django_modular_user.user:PasswordMixin',
	'django_modular_user.user:ActiveMixin',
	'django_modular_user.user:StaffMixin',
	'django_modular_user.user:PermissionsMixin',
	'django_modular_user.user:LastLoginMixin',
	'django_modular_user.user:JoinedMixin',
	'django_modular_user.user:AddressMixin',
]

AUTHENTICATION_BACKENDS = (
	'django_passwords.django_backend.DjangoBackend',
)

REQUEST_USER_BACKENDS = (
	'aiakos.openid_provider.request_user:BearerTokenAuth',
	'aiakos.openid_provider.request_user:BearerTokenPostAuth',
	'aiakos.openid_provider.request_user:ClientSecretBasicAuth',
	'aiakos.openid_provider.request_user:ClientSecretPostAuth',
	'django.contrib.auth',
)

MIDDLEWARE = [
	'aiakos.health.HealthcheckMiddleware',
	'django.middleware.security.SecurityMiddleware',
	'whitenoise.middleware.WhiteNoiseMiddleware',
	'django_headers.HeadersMiddleware',
	'django_origin.OriginMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'django_www_authenticate.WWWAuthenticateMiddleware',
	'aiakos.multiuser.prepend_user.PrependUser',
]

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

ABSOLUTE_URL_OVERRIDES = {
	'auth.user': lambda u: "/%s/" % u.username,
}

ROOT_URLCONF = 'aiakos.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
				'django_extauth.context_processors.identity_providers',
				'aiakos.bootstrap.theme',
			],
		},
	},
]

WSGI_APPLICATION = 'aiakos.wsgi.application'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# Configuration

HOME_URL = os.getenv('HOME_URL', '/auth/settings/')

MEDIA_URL = os.getenv("MEDIA_URL", '/media/')

_MEDIA_PROVIDER = os.getenv("MEDIA_PROVIDER")
if _MEDIA_PROVIDER:
	DEFAULT_FILE_STORAGE = "django_extstorage." + _MEDIA_PROVIDER + ".Storage"

INSECURE_END_SESSION_ENDPOINT = os.getenv('INSECURE_END_SESSION_ENDPOINT') in ['1', 'on', 'yes', 'true']

from dj12.config import *  # isort:skip

STATIC_URL = BASE_URL + 'static/'
