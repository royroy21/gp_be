import json
from urllib.parse import parse_qs

from asgiref.sync import async_to_sync
from channels import exceptions
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from django.db.models import Count

from project.chat import models, serializers
from project.chat.consumers import common
from project.core.requests import SudoRequest
from project.gig import models as gig_models

User = get_user_model()


class NewRoomConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        self.room = None
        self.room_group_name = None
        super().__init__(*args, **kwargs)

    def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            common.log_error(
                self.scope,
                "Disconnecting, user not authenticated",
            )
            raise exceptions.DenyConnection

        self.room = self.get_or_create_room()

        # Join own room. This only exists so the
        # server can send the room id to the client.
        self.room_group_name = "new_room_%s" % user.id
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        # Send room id to connected client
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "user": common.format_user(user),
                "message": "",
            },
        )
        self.accept()

    def get_or_create_room(self):
        """
        Returns room and boolean indicating if room was created.
        """
        user = self.scope["user"]

        query_string = parse_qs(self.scope["query_string"].decode())
        _type = query_string.get("type")
        if not _type:
            common.log_error(
                self.scope,
                "Disconnecting, no type parameter",
            )
            raise exceptions.DenyConnection
        if _type[0].upper() == models.DIRECT:
            return self.get_or_create_direct_message_room(user, query_string)
        if _type[0].upper() == models.GIG:
            return self.get_or_create_gig_response_room(user, query_string)
        else:
            common.log_error(
                self.scope,
                "Disconnecting, type parameter not direct or gig",
            )
            raise exceptions.DenyConnection

    def get_or_create_direct_message_room(self, user, query_string):
        """
        Returns an existing room if one exists already for these users.
        Else creates and returns a new room.
        """
        to_user_id = query_string.get("to_user_id")
        if not to_user_id:
            common.log_error(
                self.scope,
                "Disconnecting, no to_user_id parameter",
            )
            raise exceptions.DenyConnection
        to_user_query = User.objects.filter(id=to_user_id[0])
        if not to_user_query.exists():
            common.log_error(
                self.scope,
                "Disconnecting, to_user_id not found in database",
            )
            raise exceptions.DenyConnection
        to_user = to_user_query.first()

        existing_room = self.get_direct_message_room(user, to_user)
        if existing_room:
            return existing_room

        room = models.Room.objects.create(
            user=user,
            type=models.DIRECT,
        )
        room.members.add(user, to_user)
        return room

    def get_direct_message_room(self, user, to_user):
        """
        Returns an existing direct message room only if
        the members of that room are the user and to_user.
        """
        query = (
            models.Room.objects.filter(type=models.DIRECT, active=True)
            .annotate(member_count=Count("members"))
            .filter(members=user)
            .filter(members=to_user)
            .filter(member_count=2)
        )
        return query.first()

    def get_or_create_gig_response_room(self, user, query_string):
        """
        Returns an existing room if one exists already for this gig.
        Else creates and returns a new room.
        """
        gig_id = query_string.get("gig_id")
        if not gig_id:
            common.log_error(
                self.scope,
                "Disconnecting, no gig_id parameter",
            )
            raise exceptions.DenyConnection
        gig_query = gig_models.Gig.objects.filter(id=gig_id[0])
        if not gig_query.exists():
            common.log_error(
                self.scope,
                "Disconnecting, gig_id not found in database",
            )
            raise exceptions.DenyConnection
        gig = gig_query.first()

        existing_room = self.get_gig_response_room(user, gig)
        if existing_room:
            return existing_room

        room = models.Room.objects.create(
            user=user,
            type=models.GIG,
            gig=gig,
        )
        room.members.add(user, gig.user)
        return room

    def get_gig_response_room(self, user, gig):
        query = models.Room.objects.filter(
            user=user,
            gig=gig,
            type=models.GIG,
            active=True,
        )
        return query.first()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def chat_message(self, event):
        """
        Receives message from room group.
        Broadcasts message via websocket.
        """
        request = SudoRequest(user=self.scope["user"])
        room_serialized = serializers.RoomSerializer(
            self.room,
            context={"request": request},
        )
        self.send(
            text_data=json.dumps(
                {
                    "room": room_serialized.data,
                    "user": event["user"],
                    "message": event["message"],
                }
            )
        )
