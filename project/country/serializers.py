from rest_framework import serializers

from project.country import models


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CountryCode
        fields = ("id", "country", "code")

    def to_internal_value(self, data):
        return models.CountryCode.objects.get(**data)
