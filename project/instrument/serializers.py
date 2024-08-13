from django.core import exceptions as django_exceptions
from rest_framework import serializers

from project.instrument import models


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instrument
        fields = (
            "id",
            "instrument",
        )

    def to_internal_value(self, data):
        try:
            return models.Instrument.objects.get(**data)
        except models.Instrument.DoesNotExist:
            raise serializers.ValidationError({"Instruments do not exist"})
        except django_exceptions.FieldError:
            raise serializers.ValidationError("Invalid Instruments")
