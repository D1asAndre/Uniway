"""
ASGI config for djangoProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os


from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()
import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import apps.room.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()
application = ProtocolTypeRouter({
    "https": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            apps.room.routing.websocket_urlpatterns
        )
    )
})