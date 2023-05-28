from django.urls import re_path

from project.chat import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/new_chat/",
        consumers.new_room.NewRoomConsumer.as_asgi()
    ),
    re_path(
        r"ws/chat/(?P<room_id>\w+)/",
        consumers.existing_room.ExistingRoomConsumer.as_asgi()
    ),
]
