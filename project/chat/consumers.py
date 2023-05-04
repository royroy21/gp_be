import json
from urllib.parse import parse_qs

from asgiref.sync import async_to_sync
from channels import exceptions
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model

from project.chat import models
from project.gig import models as gig_models

User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        # These are for sending messages to everyone in the room.
        self.room = None
        self.room_group_name = None

        # This is for sending messages to the single connecting client.
        self.own_room_group_name = None

        super().__init__(*args, **kwargs)

    def connect(self):
        if not self.scope["user"].is_authenticated:
            raise exceptions.DenyConnection

        # Join group room
        self.room, room_created = self.get_or_create_room()
        self.room_group_name = "chat_%s" % self.room
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

        if room_created:
            # Join own room. This only exists so the
            # server can send the room id to the client.
            self.own_room_group_name = "websocket_%s" % self.scope["user"].id
            async_to_sync(self.channel_layer.group_add)(
                self.own_room_group_name, self.channel_name
            )

            # Send room id to connected client
            async_to_sync(self.channel_layer.group_send)(
                self.own_room_group_name,
                {"type": "chat_message", "message": ""},
            )

    def get_or_create_room(self):
        """
        Returns room and boolean indicating if room was created.
        """
        room_id = self.scope["url_route"]["kwargs"]["room_id"]
        user = self.scope["user"]
        room_created = False

        if room_id == "new":
            room_created = True
            query_string = parse_qs(self.scope["query_string"].decode())
            _type = query_string.get("type")
            if not _type:
                raise exceptions.DenyConnection
            if _type[0].upper() == models.DIRECT:
                return (
                    self.create_direct_message_room(user, query_string),
                    room_created,
                )
            if _type[0].upper() == models.GIG:
                return (
                    self.create_gig_response_room(user, query_string),
                    room_created,
                )
            else:
                raise exceptions.DenyConnection
        else:
            return self.get_room(room_id), room_created

    def create_direct_message_room(self, user, query_string):
        to_user_id = query_string.get("to_user_id")
        if not to_user_id:
            raise exceptions.DenyConnection
        to_user_query = User.objects.filter(id=to_user_id[0])
        if not to_user_query.exists():
            raise exceptions.DenyConnection
        to_user = to_user_query.first()
        room = models.Room.objects.create(
            user=user,
            type=models.DIRECT,
        )
        room.members.add(user, to_user)
        return room.id

    def create_gig_response_room(self, user, query_string):
        gig_id = query_string.get("gig_id")
        if not gig_id:
            raise exceptions.DenyConnection
        gig_query = gig_models.Gig.objects.filter(id=gig_id[0])
        if not gig_query.exists():
            raise exceptions.DenyConnection
        gig = gig_query.first()
        room = models.Room.objects.create(
            user=user,
            type=models.GIG,
            gig=gig,
        )
        room.members.add(user, gig.user)
        return room.id

    def get_room(self, room_id):
        try:
            parsed_room_id = int(room_id)
        except ValueError:
            raise exceptions.DenyConnection

        room_query = models.Room.objects.filter(id=parsed_room_id)
        if not room_query.exists():
            raise exceptions.DenyConnection

        return room_query.first().id

    def disconnect(self, close_code):
        if not self.room_group_name:
            return

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        message = json.loads(text_data)["message"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]
        user = self.scope["user"]

        if message:
            models.Message.objects.create(
                user=user,
                room=models.Room.objects.get(id=self.room),
                content=message,
            )

        # Send message to WebSocket
        self.send(
            text_data=json.dumps(
                {
                    "room": self.room,
                    "user": {"id": user.id, "username": user.username},
                    "message": message,
                }
            )
        )
