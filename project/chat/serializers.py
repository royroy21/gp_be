from rest_framework import serializers

from project.chat import models
from project.custom_user import serializers as user_serializers
from project.gig import serializers as gig_serializers


class MessageSerializer(serializers.ModelSerializer):
    user = user_serializers.UserSerializerSimple(read_only=True)

    class Meta:
        model = models.Message
        fields = (
            "id",
            "user",
            "message",
        )


class RoomSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    gig = gig_serializers.GigSerializer()

    class Meta:
        model = models.Room
        fields = (
            "id",
            "title",
            "gig",
            "type",
            "timestamp",
            "last_message",
            "members",
        )

    def get_title(self, room):
        """
        Either the title of the Gig if in response to a Gig or the
        username of the other user (not the requesting user) if a
        direct message.
        """
        if room.type == models.GIG:
            return room.gig.title

        # Assume room is type DIRECT
        requesting_user = self.context["request"].user
        return room.members.exclude(id=requesting_user.id).first().username

    def get_timestamp(self, room):
        """
        Date of the last message posted.
        """
        message = self.retrieve_last_message(room)
        if not message:
            return None
        return message.date_created.isoformat()

    def retrieve_last_message(self, room):
        return room.messages.order_by("date_created").last()

    def get_last_message(self, room):
        """
        Returns the last message posted.
        """
        message = self.retrieve_last_message(room)
        if not message:
            return None
        return message.message

    def get_members(self, room):
        requesting_user = self.context["request"].user
        query = room.members.exclude(id=requesting_user.id)
        return user_serializers.UserSerializerSimple(query, many=True).data
