from django.contrib.postgres import search
from django.db import models
from django.utils import timezone

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
    search_username = models.CharField(max_length=254, null=True)
    search_country = models.CharField(max_length=254, null=True)
    search_genres = models.TextField(null=True)
    search_vector = search.SearchVectorField(null=True)

    def save(self, *args, **kwargs):
        super().save()
        self.update_search_vector()
        self.user.update_search_vector()

    def update_search_vector(self):
        self.search_username = self.user.username
        self.search_country = f"{self.country.country} {self.country.code}"
        self.search_genres = " ".join(
            genre.genre for genre in self.genres.all()
        )
        # Saving here for fields to show up for SearchVector.
        super().save()
        self.search_vector = search.SearchVector(
            "search_username",
            "title",
            "description",
            "location",
            "search_country",
            "search_genres",
        )
        super().save()

    def replies(self):
        return (
            self.rooms.filter(active=True)  # noqa
            .exclude(messages__isnull=True)
            .count()
        )

    @property
    def is_past_gig(self):
        return self.start_date < timezone.now()
