from django.contrib.auth import get_user_model
from rest_framework import serializers

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


class GigSerializer(serializers.ModelSerializer):
    user = user_serializers.UserSerializerIfNotOwner()
    genre = GenreSerializer()

    class Meta:
        model = models.Gig
        fields = (
            "id",
            "user",
            "title",
            "venue",
            "location",
            "description",
            "genre",
            "start_date",
            "end_date",
        )


class GigDocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.SerializerMethodField()
    title = serializers.CharField(read_only=True)
    venue = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    genre = serializers.SerializerMethodField()
    start_date = serializers.DateField(read_only=True)
    end_date = serializers.DateField(read_only=True)

    class Meta:
        document = GigDocument
        fields = (
            "id",
            "user",
            "title",
            "venue",
            "location",
            "description",
            "genre",
            "start_date",
            "end_date",
        )

    def get_user(self, obj):
        """
        Elastic search needs this to be a string.
        Converting back to id here so to match GigSerializer.
        """
        user = User.objects.get(username=obj.user)
        return user_serializers.UserSerializerIfNotOwner(user).data

    def get_genre(self, obj):
        genre = models.Genre.objects.filter(genre=obj.genre).first()
        if genre:
            return GenreSerializer(genre).data
        else:
            return None
