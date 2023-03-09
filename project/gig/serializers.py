from copy import deepcopy

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from project.country import models as country_models
from project.country import serializers as country_serializers
from project.custom_user import serializers as user_serializers
from project.gig import models
from project.gig.search_indexes.documents.gig import GigDocument

User = get_user_model()


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Genre
        fields = (
            "id",
            "genre",
        )

    def to_internal_value(self, data):
        return models.Genre.objects.get(**data)


class GigSerializer(serializers.ModelSerializer):
    user = user_serializers.UserSerializerIfNotOwner(required=False)
    genres = GenreSerializer(many=True)
    country = country_serializers.CountrySerializer()

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
        )

    @transaction.atomic
    def create(self, validated_data):
        copy_of_validated_data = deepcopy(validated_data)
        copy_of_validated_data["user"] = self.context["request"].user
        genres = copy_of_validated_data.pop("genres")
        gig = super().create(copy_of_validated_data)
        gig.genres.add(*genres)
        return gig


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
        )

    def get_user(self, document):
        """Converting here so to match GigSerializer."""
        user = User.objects.get(username=document.user)
        return user_serializers.UserSerializerIfNotOwner(user).data

    def get_genres(self, document):
        """Converting here so to match GigSerializer."""
        return [
            GenreSerializer(models.Genre.objects.get(genre=genre)).data
            for genre in document.genres
        ]

    def get_country(self, document):
        """Converting here so to match GigSerializer."""
        country = country_models.CountryCode.objects.get(
            country=document.country,
        )
        return country_serializers.CountrySerializer(country).data
