"""
WSGI config for aiakos project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aiakos.settings")

application = get_wsgi_application()

DEBUG = bool(int(os.environ.get("DEBUG", "0")))
if DEBUG:
	from django.views import debug
	def null_technical_500_response(request, exc_type, exc_value, tb, status_code=500):
		raise exc_value.with_traceback(tb)
	debug.technical_500_response = null_technical_500_response

	from werkzeug.debug import DebuggedApplication
	application = DebuggedApplication(application, evalex=True, pin_security=False)
