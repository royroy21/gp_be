import json

from channels import exceptions
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from project.chat import models
from project.chat.consumers import common

User = get_user_model()


class ExistingRoomConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        self.room = None
        self.room_group_name = None
        super().__init__(*args, **kwargs)

    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            common.log_error(
                self.scope,
                "Disconnecting, user not authenticated",
            )
            raise exceptions.DenyConnection

        self.room = await self.get_room()
        self.room_group_name = "room_%s" % self.room.id
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

    @database_sync_to_async
    def get_room(self):
        room_id = self.scope["url_route"]["kwargs"]["room_id"]
        room_query = models.Room.objects.filter(id=room_id)
        if not room_query.exists():
            common.log_error(
                self.scope,
                "Disconnecting, room_id not found in database",
            )
            raise exceptions.DenyConnection
        return room_query.first()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Receive message from websocket.
        """
        message = json.loads(text_data)["message"]
        if not message:
            return

        user = self.scope["user"]
        message_id = await self.create_message(user, message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "user": common.format_user(user),
                "message_id": str(message_id),
                "message": message,
            },
        )

    @database_sync_to_async
    def create_message(self, user, content):
        message = models.Message.objects.create(
            user=user,
            room=models.Room.objects.get(id=self.room.id),
            message=content,
        )
        return message.id

    async def chat_message(self, event):
        """
        Receives message from room group.
        Broadcasts message via websocket.
        """
        await self.send(
            text_data=json.dumps(
                {
                    "room": str(self.room.id),
                    "user": event["user"],
                    "id": str(event["message_id"]),
                    "message": event["message"],
                }
            )
        )
