from django.core import exceptions as django_exceptions
from rest_framework import serializers

from project.genre import models


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Genre
        fields = (
            "id",
            "genre",
        )

    def to_internal_value(self, data):
        try:
            return models.Genre.objects.get(**data)
        except models.Genre.DoesNotExist:
            raise serializers.ValidationError({"Genres do not exist"})
        except django_exceptions.FieldError:
            raise serializers.ValidationError("Invalid Genres")
