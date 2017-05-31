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
	from werkzeug.debug import DebuggedApplication
	application = DebuggedApplication(application, evalex=True, pin_security=False)
