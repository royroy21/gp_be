from django.db import models

from project.core.models import BaseModel


class Genre(BaseModel):
    genre = models.CharField(max_length=254, unique=True)
    rank = models.IntegerField(default=1)
