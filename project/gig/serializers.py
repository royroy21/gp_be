from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from project.country import models as country_models
from project.country import serializers as country_serializers
from project.custom_user import serializers as user_serializers
from project.genre import models as genre_models
from project.genre import serializers as genre_serializers
from project.gig import models
from project.gig.search_indexes.documents.gig import GigDocument

User = get_user_model()


class GigSerializer(serializers.ModelSerializer):
    user = user_serializers.UserSerializerIfNotOwner(read_only=True)
    genres = genre_serializers.GenreSerializer(many=True, read_only=True)
    country = country_serializers.CountrySerializer(read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)

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
        )

    def validate(self, attrs):
        genres = self.initial_data.pop("genres", None)
        if genres is not None:
            attrs["genres"] = genre_serializers.GenreSerializer(
                data=genres, many=True
            ).to_internal_value(data=genres)

        country = self.initial_data.pop("country", None)
        if country is not None:
            attrs["country"] = country_serializers.CountrySerializer(
                data=country
            ).to_internal_value(data=country)

        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data):
        copy_of_validated_data = self.copy_data(validated_data)
        genres = copy_of_validated_data.pop("genres", None)
        gig = super().create(copy_of_validated_data)
        if genres is not None:
            gig.genres.clear()
            gig.genres.add(*genres)
        return gig

    @transaction.atomic
    def update(self, instance, validated_data):
        copy_of_validated_data = self.copy_data(validated_data)
        genres = copy_of_validated_data.pop("genres", [])
        gig = super().update(instance, copy_of_validated_data)
        gig.genres.clear()
        gig.genres.add(*genres)
        return gig

    def copy_data(self, data):
        # Copying like this as deepcopy doesn't like in memory files.
        data_copy = {
            key: value for key, value in data.items() if key != "image"
        }
        data_copy["user"] = self.context["request"].user
        if "image" in data.keys():
            # Adding like this as we need to preserve None for
            # images as this indicates an image to be removed.
            data_copy["image"] = data["image"]
        return data_copy


class GigDocumentSerializer(serializers.Serializer):
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
        )

    def get_user(self, document):
        """Converting here so to match GigSerializer."""
        user = User.objects.get(username=document.user)
        return user_serializers.UserSerializerIfNotOwner(
            user,
            context=self.context,
        ).data

    def get_genres(self, document):
        """Converting here so to match GigSerializer."""
        return [
            genre_serializers.GenreSerializer(
                genre_models.Genre.objects.get(genre=genre)
            ).data
            for genre in document.genres
        ]

    def get_country(self, document):
        """Converting here so to match GigSerializer."""
        country = country_models.CountryCode.objects.get(
            country=document.country,
        )
        return country_serializers.CountrySerializer(country).data

    def get_image(self, document):
        """Converting here to get full image URL with domain."""
        if not document.image:
            return None
        return self.context["request"].build_absolute_uri(document.image)
