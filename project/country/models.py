# type: ignore
# TODO - mypy with django-stubs is having trouble with abstract classes.
# Check if future versions has corrected this :/
from django.db import models

from project.core.models import BaseModel


class CountryCode(BaseModel):
    country = models.CharField(max_length=254, unique=True)
    code = models.CharField(max_length=2, unique=True)
    rank = models.IntegerField(default=2)

    def __str__(self):
        return f"{self.country} ({self.code})"