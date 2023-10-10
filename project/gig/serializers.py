from django.contrib.auth import get_user_model
from django.core import exceptions as django_exceptions
from django.db import transaction
from rest_framework import serializers

from project.audio import models as audio_models
from project.country import models as country_models
from project.country import serializers as country_serializers
from project.custom_user import serializers as user_serializers
from project.genre import models as genre_models
from project.genre import serializers as genre_serializers
from project.gig import models
from project.gig.search_indexes.documents.gig import GigDocument
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


class GigDocumentSerializer(serializers.Serializer):  # noqa
    id = serializers.IntegerField(read_only=True)
    user = serializers.SerializerMethodField()
    title = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)
    country = serializers.SerializerMethodField()
    description = serializers.CharField(read_only=True)
    genres = serializers.SerializerMethodField()
    has_spare_ticket = serializers.BooleanField(read_only=True)
    start_date = serializers.DateField(read_only=True)
    end_date = serializers.DateField(read_only=True)
    image = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        document = GigDocument
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
        )

    def get_user(self, document):
        """Converting here so to match GigSerializer."""
        user = User.objects.get(username=document.user)
        return user_serializers.UserSerializerIfNotOwner(
            user,
            context=self.context,
        ).data

    def get_country(self, document):  # noqa
        """Converting here so to match GigSerializer."""
        country = country_models.CountryCode.objects.filter(
            country=document.country,
        ).first()
        if not country:
            return None
        return country_serializers.CountrySerializer(country).data

    def get_genres(self, document):  # noqa
        """Converting here so to match GigSerializer."""
        return [
            genre_serializers.GenreSerializer(
                genre_models.Genre.objects.get(genre=genre)
            ).data
            for genre in document.genres
        ]

    def get_image(self, document):
        """Converting here to get full image URL with domain."""
        if not document.image:
            return None
        return self.context["request"].build_absolute_uri(document.image)

    def get_thumbnail(self, document):
        """Converting here to get full thumbnail URL with domain."""
        if not document.thumbnail:
            return None
        return self.context["request"].build_absolute_uri(document.thumbnail)

    def get_is_favorite(self, document):
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        return user.favorite_gigs.filter(id=document.id).exists()

    def get_replies(self, document):
        return document.replies
