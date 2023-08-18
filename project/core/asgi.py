"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os
import sys

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# Defining here to stop `Apps aren't loaded yet` error.
sys.path.append("/code/project/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings.local")
django_asgi_app = get_asgi_application()

from project.chat import routing  # noqa
from project.middleware import token  # noqa

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": token.TokenAuthMiddlewareStack(
            URLRouter(routing.websocket_urlpatterns)
        ),
    }
)
