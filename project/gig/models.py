from django.db import models

from project.core.models import BaseModel


class Gig(BaseModel):
    user = models.ForeignKey(
        "custom_user.User",
        on_delete=models.CASCADE,
        related_name="gigs",
    )
    title = models.CharField(
        max_length=254,
        help_text="title, artist, band or festival",
    )
    description = models.TextField(default="", blank=True)
    location = models.CharField(
        max_length=254,
        help_text="Venue, pub, warehouse or location",
    )
    country = models.ForeignKey(
        "country.CountryCode",
        on_delete=models.CASCADE,
        related_name="gigs",
    )
    genres = models.ManyToManyField(
        "genre.Genre",
        blank=True,
        related_name="gigs",
    )
    has_spare_ticket = models.BooleanField(default=False)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
    )
    image = models.ImageField(
        upload_to="gig",
        blank=True,
        null=True,
    )
    thumbnail = models.ImageField(
        upload_to="gig",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.title}, {self.user.get_username()}"

    @property
    def genres_indexing(self):
        """Used in Elasticsearch indexing."""
        return [genre.genre for genre in self.genres.filter(active=True)]
