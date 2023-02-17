# type: ignore
# TODO - mypy with django-stubs is having trouble with abstract classes.
# Check if future versions has corrected this :/
from django.db import models

from project.core.models import BaseModel


class Genre(BaseModel):
    genre = models.CharField(max_length=254, unique=True)
    rank = models.IntegerField(default=1)

    def __str__(self):
        return self.genre


class Gig(BaseModel):
    user = models.ForeignKey(
        "custom_user.User",
        on_delete=models.CASCADE,
        related_name="gigs",
    )
    title = models.CharField(max_length=254)
    artist = models.CharField(max_length=254)
    venue = models.CharField(max_length=254)
    location = models.CharField(max_length=254)
    country = models.ForeignKey(
        "country.CountryCode",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="gigs",
    )
    description = models.TextField(default="", blank=True)
    genres = models.ManyToManyField(
        "gig.Genre",
        blank=True,
        related_name="gigs",
    )
    has_spare_ticket = models.BooleanField(default=False)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(default=None, blank=True, null=True)

    def __str__(self):
        return f"{self.title}, {self.user.get_username()}"

    @property
    def genres_indexing(self):
        """Used in Elasticsearch indexing."""
        return [genre.genre for genre in self.genres.all()]
