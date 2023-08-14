from django.db import models

from project.core.models import BaseModel


class CountryCode(BaseModel):
    country = models.CharField(max_length=254, unique=True)
    code = models.CharField(max_length=2, unique=True)
    rank = models.IntegerField(default=2)
