import os

import dj_database_url
import dj_email_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
assert SECRET_KEY, "Non-empty DJANGO_SECRET_KEY environment variable is required!"

DEBUG = os.getenv("DEBUG") == "1"

HOSTNAME = os.getenv("AIAKOS_HOSTNAME", "")
ALLOWED_HOSTS = [HOSTNAME.split(":")[0]]

if os.getenv("USE_X_FORWARDED_PROTO", "") == "1":
	SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_SSL_REDIRECT = True if not DEBUG else False

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

	'django_profile_oidc',
	'django_extauth',
	'django_passwords',
	'aiakos.openid_provider',
	'aiakos',
]

AUTHENTICATION_BACKENDS = (
	'django_passwords.django_backend.DjangoBackend',
)

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'aiakos.openid_provider.middleware.BearerTokenAuth',
	'aiakos.openid_provider.middleware.ClientSecretBasicAuth',
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

STATIC_URL = 'https://storage.googleapis.com/djangocdn/1.10/'
