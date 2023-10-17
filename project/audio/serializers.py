from django.db import transaction
from django.db.models import F
from rest_framework import serializers

from project.audio import models
from project.custom_user import serializers as user_serializers
from project.genre import serializers as genre_serializers
from project.gig import serializers as gig_serializers
from project.image import tasks as image_tasks


class AudioSerializer(serializers.ModelSerializer):
    user = user_serializers.UserSerializerIfNotOwner(read_only=True)

    class Meta:
        model = models.Audio
        fields = (
            "id",
            "title",
            "position",
            "image",
            "thumbnail",
            "file",
            "album",
            "user",
        )

    @transaction.atomic
    def create(self, validated_data):
        copy_of_validated_data = self.copy_data(validated_data)
        self.calculate_new_track_positions(
            new_position=copy_of_validated_data["position"],
            album=copy_of_validated_data["album"],
        )
        audio = super().create(copy_of_validated_data)
        if copy_of_validated_data.get("image", None) is not None:
            image_tasks.create_thumbnail.delay("audio", "audio", audio.id)

        self.reinitialize_track_positions(copy_of_validated_data["album"])
        return audio

    @transaction.atomic
    def update(self, instance, validated_data):
        copy_of_validated_data = self.copy_data(validated_data)
        self.calculate_new_track_positions(
            new_position=copy_of_validated_data["position"],
            album=instance.album,
        )
        audio = super().update(instance, copy_of_validated_data)
        if copy_of_validated_data.get("image", None) is not None:
            image_tasks.create_thumbnail.delay("audio", "audio", audio.id)

        self.reinitialize_track_positions(instance.album)
        return audio

    def copy_data(self, data):
        # Copying like this as deepcopy doesn't like in memory files.
        data_copy = {
            key: value
            for key, value in data.items()
            if key not in ["image", "file"]
        }
        data_copy["user"] = self.context["request"].user
        if "image" in data:
            # Adding like this as we need to preserve None for
            # files as this indicates a file to be removed.
            data_copy["image"] = data["image"]
            # Removing thumbnail here as the create_thumbnail
            # task will update it. Or if image is deleted also
            # delete thumbnail.
            data_copy["thumbnail"] = None

        if "file" in data:
            data_copy["file"] = data["file"]

        return data_copy

    def calculate_new_track_positions(self, new_position, album):
        """
        If an existing track is found to have the same position
        as the new position, tracks matching this position and
        after are bumped up one position.
        """
        clashing_track = album.audio_tracks.filter(
            position=new_position,
            active=True,
        ).first()
        if not clashing_track:
            return

        tracks_to_amend = album.audio_tracks.filter(
            position__gte=new_position,
            active=True,
        )
        tracks_to_amend.update(position=F("position") + 1)

    @staticmethod
    def reinitialize_track_positions(album):
        """
        Sets track positions back to 1,2,3,4 etc.
        Useful if track positions get messy due to continual
        adding and deleting of tracks from an album.
        """
        tracks = album.audio_tracks.filter(active=True).order_by("position")
        for new_position, track in enumerate(tracks, 1):
            track.position = new_position
            track.save()


class AlbumSerializer(serializers.ModelSerializer):
    user = user_serializers.UserSerializerIfNotOwner(read_only=True)
    profile = user_serializers.UserSerializerWithSimplifiedToInternalValue(
        required=False,
    )
    genres = genre_serializers.GenreSerializer(many=True)
    gig = gig_serializers.GigSerializerWithSimplifiedToInternalValue(
        required=False
    )
    is_default = serializers.BooleanField(read_only=True)
    tracks = serializers.SerializerMethodField()
    number_of_tracks = serializers.SerializerMethodField()

    class Meta:
        model = models.Album
        fields = (
            "id",
            "title",
            "description",
            "genres",
            "image",
            "thumbnail",
            "profile",
            "gig",
            "user",
            "is_default",
            "tracks",
            "number_of_tracks",
        )

    @transaction.atomic
    def create(self, validated_data):
        copy_of_validated_data = self.copy_data(validated_data)
        genres = copy_of_validated_data.pop("genres", None)
        album = super().create(copy_of_validated_data)
        if genres is not None:
            album.genres.clear()
            album.genres.add(*genres)
        if copy_of_validated_data.get("image", None) is not None:
            image_tasks.create_thumbnail.delay("audio", "album", album.id)
        return album

    @transaction.atomic
    def update(self, instance, validated_data):
        copy_of_validated_data = self.copy_data(validated_data)
        genres = copy_of_validated_data.pop("genres", None)
        album = super().update(instance, copy_of_validated_data)
        if genres is not None:
            album.genres.clear()
            album.genres.add(*genres)
        if copy_of_validated_data.get("image", None) is not None:
            image_tasks.create_thumbnail.delay("audio", "album", album.id)
        return album

    def copy_data(self, data):
        # Copying like this as deepcopy doesn't like in memory files.
        data_copy = {
            key: value for key, value in data.items() if key != "image"
        }
        data_copy["user"] = self.context["request"].user
        if "image" in data:
            # Adding like this as we need to preserve None for
            # images as this indicates an image to be removed.
            data_copy["image"] = data["image"]
            # Removing thumbnail here as the create_thumbnail
            # task will update it. Or if image is deleted also
            # delete thumbnail.
            data_copy["thumbnail"] = None

        return data_copy

    def get_tracks(self, album):
        if not album.audio_tracks.filter(active=True).exists():
            return []

        data = AudioSerializer(
            album.audio_tracks.filter(active=True),
            many=True,
            context=self.context,
        ).data
        return sorted(data, key=lambda track: track["position"])

    def get_number_of_tracks(self, album):
        return album.audio_tracks.filter(active=True).count()
