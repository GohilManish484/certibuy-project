"""WSGI config for certibuy project."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "certibuy.settings")

application = get_wsgi_application()
