from typing import Dict

from django.contrib.gis.geos import Point
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class LocationField(serializers.Field):
    default_error_messages = {
        "invalid": _("Invalid format"),
    }

    def to_representation(self, value: Point) -> Dict:
        return {"latitude": value.coords[1], "longitude": value.coords[0]}

    def to_internal_value(self, value: Dict) -> Point:
        if not isinstance(value, dict):
            self.fail("invalid")
        if sorted(value.keys()) != ["latitude", "longitude"]:
            self.fail("invalid")
        if not (
            isinstance(value["latitude"], float)
            and isinstance(value["longitude"], float)
        ):
            self.fail("invalid")
        return Point(value["longitude"], value["latitude"])
