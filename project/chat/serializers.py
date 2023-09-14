from django.db import transaction
from rest_framework import serializers

from project.chat import models
from project.chat.search_indexes.documents.room import RoomDocument
from project.custom_user import serializers as user_serializers
from project.gig import serializers as gig_serializers
from project.site import domain


class MessageSerializer(serializers.ModelSerializer):
    user = user_serializers.UserSerializerIfNotOwner(read_only=True)

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
    image = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    user = user_serializers.UserSerializerIfNotOwner(read_only=True)

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
            "image",
            "thumbnail",
            "user",
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
        return user_serializers.UserSerializerIfNotOwner(
            query,
            many=True,
            context=self.context,
        ).data

    def get_image(self, room):
        """
        Returns the image for the gig if the room is of that type.
        Otherwise, returns the image for the first member of the
        room excluding the requesting user.
        """
        if room.gig:
            return (
                domain.build_absolute_uri(room.gig.image.url)
                if room.gig.image
                else None
            )
        else:
            requesting_user = self.context["request"].user
            # TODO - returning first member excluding requesting user.
            # The order of the query might change if more members are
            # added. This would result in the image changing which is
            # not desirable. Check logic again when more members are
            # added to a room.
            member = room.members.exclude(id=requesting_user.id).first()
            if member:
                return (
                    domain.build_absolute_uri(member.image.url)
                    if member.image
                    else None
                )
        return None

    def get_thumbnail(self, room):
        """
        Returns the thumbnail for the gig if the room is of that type.
        Otherwise, returns the thumbnail for the first member of the
        room excluding the requesting user.
        """
        if room.gig:
            return (
                domain.build_absolute_uri(room.gig.thumbnail.url)
                if room.gig.thumbnail
                else None
            )
        else:
            requesting_user = self.context["request"].user
            # TODO - returning first member excluding requesting user.
            # The order of the query might change if more members are
            # added. This would result in the thumbnail changing which is
            # not desirable. Check logic again when more members are
            # added to a room.
            member = room.members.exclude(id=requesting_user.id).first()
            if member:
                return (
                    domain.build_absolute_uri(member.thumbnail.url)
                    if member.thumbnail
                    else None
                )
        return None

    def validate(self, data):
        members = self.initial_data.get("members")
        if members:
            # TODO - fix this dodgy code. Hacky I know. It's late :(
            # No validation here. Use a stripped down user serializer.
            data["members"] = [member["id"] for member in members]

        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Currently can only update membership.
        """
        members = validated_data.get("members")
        if members:
            instance.members.clear()
            instance.members.add(self.context["request"].user, *members)

        return instance


class RoomDocumentSerializer(serializers.Serializer):  # noqa
    id = serializers.IntegerField(read_only=True)
    title = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    gig = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        # Saving all objects here in dictionary,
        # so we don't keep querying the database
        # for room objects.
        self.objects = {
            document["id"]: models.Room.objects.get(id=document["id"])
            for document in args[0]
        }
        super().__init__(*args, **kwargs)

    class Meta:
        document = RoomDocument
        fields = (
            "id",
            "title",
            "timestamp",
            "last_message",
            "members",
            "gig",
            "image",
            "thumbnail",
            "user",
        )

    def get_standard_serializer(self, document):
        """
        This returns an initiated RoomSerializer.
        This is used so this serializer returns
        data in the same format as RoomSerializer.
        """
        return RoomSerializer(
            self.objects[document["id"]],
            context={"request": self.context["request"]},
        )

    def get_title(self, document):
        return self.get_standard_serializer(document).data["title"]

    def get_timestamp(self, document):
        return self.get_standard_serializer(document).data["timestamp"]

    def get_last_message(self, document):
        return self.get_standard_serializer(document).data["last_message"]

    def get_members(self, document):
        return self.get_standard_serializer(document).data["members"]

    def get_gig(self, document):
        return self.get_standard_serializer(document).data["gig"]

    def get_image(self, document):
        return self.get_standard_serializer(document).data["image"]

    def get_thumbnail(self, document):
        return self.get_standard_serializer(document).data["thumbnail"]

    def get_user(self, document):
        return self.get_standard_serializer(document).data["user"]
