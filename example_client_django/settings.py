import os

# Remove these if you're forking this app for non-example purposes.
os.environ.setdefault("DJANGO_SECRET_KEY", "qwerty")
os.environ.setdefault("DEBUG", "1")
os.environ.setdefault("ALLOWED_HOSTS", "*")

os.environ.setdefault("AUTH_SERVER", "http://auth:8000/")
os.environ.setdefault("AUTH_CLIENT_ID", "919037")
os.environ.setdefault("AUTH_CLIENT_SECRET", "32a7bb81fffd18e928109ac6155b165efdcc32ca2890e3aedaeb45cb")

import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
assert SECRET_KEY, "Non-empty DJANGO_SECRET_KEY environment variable is required!"

DEBUG = os.getenv("DEBUG") == "1"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

if os.getenv("USE_X_FORWARDED_PROTO", "") == "1":
	SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

LANGUAGE_CODE = os.getenv("LANG", 'en-us')

DATABASES = {
	'default': dj_database_url.config(conn_max_age=600, default="sqlite:///" + os.path.join(BASE_DIR, 'example.sqlite3'))
}

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

# Application definition

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django_auth_oidc',
	'raven.contrib.django.raven_compat',
]

AUTHENTICATION_BACKENDS = (
	'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

LOGIN_REDIRECT_URL = '/'

ABSOLUTE_URL_OVERRIDES = {
	'auth.user': lambda u: "/%s/" % u.username,
}

ROOT_URLCONF = 'example_client_django.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [os.path.join(BASE_DIR, "example_client_django/templates")],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

WSGI_APPLICATION = 'example_client_django.wsgi.application'

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = 'https://storage.googleapis.com/djangocdn/1.10/'
MEDIA_URL = '/media/'
