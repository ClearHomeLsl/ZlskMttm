# routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # WebSocket连接路径
    re_path(r'ws/kline/$', consumers.KlineConsumer.as_asgi()),
]