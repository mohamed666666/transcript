"""
ASGI config for audio project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""


import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import members.routing  # Import your app's WebSocket routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'audio.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        members.routing.websocket_urlpatterns  # Include your WebSocket routing here
    ),
})