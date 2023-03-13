from django.core import exceptions as django_exceptions
from rest_framework import serializers

from project.country import models


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CountryCode
        fields = ("id", "country", "code")

    def to_internal_value(self, data):
        try:
            return models.CountryCode.objects.get(**data)
        except models.CountryCode.DoesNotExist:
            raise serializers.ValidationError({"Country does not exist"})
        except django_exceptions.FieldError:
            raise serializers.ValidationError("Invalid Country")
