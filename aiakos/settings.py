import os
from urllib.parse import urlsplit

import dj_database_url
import dj_email_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
assert SECRET_KEY, "Non-empty DJANGO_SECRET_KEY environment variable is required!"

if os.getenv("USE_X_FORWARDED_PROTO", "") == "1":
	SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DEBUG = os.getenv("DEBUG") == "1"
if DEBUG:
	DEBUG_PROPAGATE_EXCEPTIONS = True

BASE_URL = os.environ.get('BASE_URL', '')

if BASE_URL:
	base_url = urlsplit(BASE_URL)

	ALLOWED_HOSTS = [base_url.hostname]

	if base_url.scheme == 'https':
		SECURE_SSL_REDIRECT = True

LANGUAGE_CODE = os.getenv("LANG", 'en-us')

DATABASES = {
	'default': dj_database_url.config(conn_max_age=600, default="sqlite:///" + os.path.join(BASE_DIR, 'db.sqlite3'))
}

HOME_URL = os.getenv('HOME_URL', '/apps/')

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'handlers': {
		'console': {
			'class': 'logging.StreamHandler',
		},
	},
	'loggers': {
		'django': {
			'handlers': ['console'],
			'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
		},
		'aiakos': {
			'handlers': ['console'],
			'level': 'DEBUG' if DEBUG else 'INFO',
		},
	},
}

RAVEN_CONFIG = {
	'dsn': os.getenv("RAVEN_URL"),
}

MEDIA_URL = os.getenv("MEDIA_URL", '/media/')

_MEDIA_PROVIDER = os.getenv("MEDIA_PROVIDER")
if _MEDIA_PROVIDER:
	DEFAULT_FILE_STORAGE = "django_extstorage." + _MEDIA_PROVIDER + ".Storage"

_EMAIL_CONFIG = dj_email_url.config(default="console://")
EMAIL_FILE_PATH = _EMAIL_CONFIG['EMAIL_FILE_PATH']
EMAIL_HOST_USER = _EMAIL_CONFIG['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = _EMAIL_CONFIG['EMAIL_HOST_PASSWORD']
EMAIL_HOST = _EMAIL_CONFIG['EMAIL_HOST']
EMAIL_PORT = _EMAIL_CONFIG['EMAIL_PORT']
EMAIL_BACKEND = _EMAIL_CONFIG['EMAIL_BACKEND']
EMAIL_USE_TLS = _EMAIL_CONFIG['EMAIL_USE_TLS']
EMAIL_USE_SSL = _EMAIL_CONFIG['EMAIL_USE_SSL']

DEFAULT_FROM_EMAIL = os.getenv('EMAIL_FROM', "webmaster@localhost")

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
	'django_modular_user.user:FullNameMixin',
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
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'django_headers.HeadersMiddleware',
	'django_www_authenticate.WWWAuthenticateMiddleware',
]

LOGIN_REDIRECT_URL = '/'

ABSOLUTE_URL_OVERRIDES = {
	'auth.user': lambda u: "/%s/" % u.username,
}

ROOT_URLCONF = 'aiakos.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [os.path.join(BASE_DIR, "aiakos/templates")],
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

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = BASE_URL + 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
