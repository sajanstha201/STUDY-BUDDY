from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path(r'ws/chat/<int:room_id>/',
         consumers.ChatRoomConsumer.as_asgi()),
]
