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

    def genres_indexing(self):
        """Used in Elasticsearch indexing."""
        # Must be a list as elastic search cannot serialize a queryset.
        return list(
            self.genres.filter(active=True).values_list("genre", flat=True)
        )

    def country_indexing(self):
        """Used in Elasticsearch indexing."""
        if not self.country:
            return None
        return f"{self.country.country} {self.country.code}"  # noqa

    def replies(self):
        return (
            self.rooms.filter(active=True)  # noqa
            .exclude(messages__isnull=True)
            .count()
        )

    def has_replies(self):
        return (
            self.rooms.filter(active=True)  # noqa
            .exclude(messages__isnull=True)
            .exists()
        )
