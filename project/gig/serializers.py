from django.contrib.auth import get_user_model
from django.core import exceptions as django_exceptions
from django.db import transaction
from rest_framework import serializers

from project.audio import models as audio_models
from project.country import serializers as country_serializers
from project.custom_user import serializers as user_serializers
from project.genre import serializers as genre_serializers
from project.gig import models
from project.image import tasks as image_tasks

User = get_user_model()


class GigSerializer(serializers.ModelSerializer):
    user = user_serializers.UserSerializerIfNotOwner(read_only=True)
    genres = genre_serializers.GenreSerializer(many=True, required=False)
    country = country_serializers.CountrySerializer()
    image = serializers.ImageField(required=False, allow_null=True)
    thumbnail = serializers.ImageField(read_only=True)
    is_favorite = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    active = serializers.BooleanField(read_only=True)

    class Meta:
        model = models.Gig
        fields = (
            "id",
            "user",
            "title",
            "location",
            "country",
            "description",
            "genres",
            "has_spare_ticket",
            "start_date",
            "end_date",
            "image",
            "thumbnail",
            "is_favorite",
            "replies",
            "active",
        )

    @transaction.atomic
    def create(self, validated_data):
        copy_of_validated_data = self.copy_data(validated_data)
        genres = copy_of_validated_data.pop("genres", None)
        gig = super().create(copy_of_validated_data)
        if genres is not None:
            gig.genres.add(*genres)
        audio_models.Album.create_default_album_for_gig(
            gig=gig,
            user=gig.user,
        )
        if copy_of_validated_data.get("image", None) is not None:
            image_tasks.create_thumbnail.delay("gig", "gig", gig.id)
        return gig

    @transaction.atomic
    def update(self, instance, validated_data):
        copy_of_validated_data = self.copy_data(validated_data)
        genres = copy_of_validated_data.pop("genres", None)
        gig = super().update(instance, copy_of_validated_data)
        if genres is not None:
            gig.genres.clear()
            gig.genres.add(*genres)
        if copy_of_validated_data.get("image", None) is not None:
            image_tasks.create_thumbnail.delay("gig", "gig", gig.id)
        return gig

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

    def get_is_favorite(self, instance):
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        return user.favorite_gigs.filter(id=instance.id).exists()

    def get_replies(self, instance):
        return instance.replies()


class GigSerializerWithSimplifiedToInternalValue(GigSerializer):
    """
    Used in other serializers to get the gig object.
    """

    def to_internal_value(self, data):
        try:
            return models.Gig.objects.get(id=data.get("id"))
        except models.Gig.DoesNotExist:
            raise serializers.ValidationError({"Gig does not exist"})
        except django_exceptions.FieldError:
            raise serializers.ValidationError("Invalid data")
