from enum import Enum

from django.contrib.gis.geos import Point
from geopy.distance import distance as geopy_distance


class Units(Enum):
    KILOMETERS = "kilometers"
    MILES = "miles"


def get_distance_between_points(
    point_1: Point,
    point_2: Point,
    units: Units,
) -> float:
    """
    Returns the distance between two Python Point objects.
    Units specified should be `miles` or `kilometers`.
    """
    distance = geopy_distance(point_1, point_2)
    if units == Units.MILES.value:
        return distance.miles
    else:
        return distance.kilometers
