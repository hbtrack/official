"""
ASGI config — HB Track
Suporta HTTP (Django Ninja) e WebSocket (Django Channels).
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

django_asgi_app = get_asgi_application()

# Import após setup do Django para evitar AppRegistryNotReady
def _get_websocket_application():
    from notifications.routing import websocket_urlpatterns
    from notifications.middleware import TokenAuthMiddlewareStack
    return AllowedHostsOriginValidator(
        TokenAuthMiddlewareStack(URLRouter(websocket_urlpatterns))
    )

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": _get_websocket_application(),
    }
)
