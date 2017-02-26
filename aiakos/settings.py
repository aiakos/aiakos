import os
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
assert SECRET_KEY, "Non-empty DJANGO_SECRET_KEY environment variable is required!"

DEBUG = os.getenv("DEBUG") == "1"

HOSTNAME = os.getenv("AIAKOS_HOSTNAME", "")
ALLOWED_HOSTS = [HOSTNAME.split(":")[0]]

if os.getenv("USE_X_FORWARDED_PROTO", "") == "1":
	SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

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
	},
}

RAVEN_CONFIG = {
    'dsn': os.getenv("RAVEN_URL"),
}

MEDIA_URL = os.getenv("MEDIA_URL", '/media/')

_MEDIA_PROVIDER = os.getenv("MEDIA_PROVIDER")
if _MEDIA_PROVIDER:
	DEFAULT_FILE_STORAGE = "django_extstorage." + _MEDIA_PROVIDER + ".Storage"

# Application definition

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'crispy_forms',
	'django_profile_oidc',
	'django_extauth',
	'raven.contrib.django.raven_compat',
	'aiakos.openid_provider',
]

AUTHENTICATION_BACKENDS = (
	'aiakos.auth_backend.BetterAuthBackend',
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
