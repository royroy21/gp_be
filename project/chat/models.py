from django.contrib.postgres import search
from django.db import models

from project.core.models import BaseModel

DIRECT = "DIRECT"
GIG = "GIG"
TYPE_CHOICES = (
    (DIRECT, "Direct message"),
    (GIG, "Reply to gig"),
)


class Room(BaseModel):

    user = models.ForeignKey(
        "custom_user.User",
        on_delete=models.CASCADE,
        related_name="rooms_created",
    )
    members = models.ManyToManyField(
        "custom_user.User",
        related_name="rooms_membership",
    )
    type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default=DIRECT,
    )
    gig = models.ForeignKey(
        "gig.Gig",
        on_delete=models.CASCADE,
        related_name="rooms",
        null=True,
    )
    search_username = models.CharField(max_length=254, null=True)
    search_members = models.TextField(null=True)
    search_gig_title = models.CharField(max_length=254, null=True)
    search_gig_description = models.TextField(null=True)
    search_gig_location = models.CharField(max_length=254, null=True)
    search_gig_country = models.CharField(max_length=254, null=True)
    search_gig_genres = models.TextField(null=True)
    search_vector = search.SearchVectorField(null=True)

    def save(self, *args, **kwargs):
        super().save()
        self.update_search_vector()

    def update_search_vector(self):
        self.search_username = self.user.username
        self.search_members = " ".join(
            member.username
            for member in self.members.all().exclude(id=self.user.id)
        )
        if self.gig:
            self.search_gig_title = self.gig.title  # noqa
            self.search_gig_description = self.gig.description  # noqa
            self.search_gig_location = self.gig.location  # noqa
            self.search_gig_country = (
                f"{self.gig.country.country} {self.gig.country.code}"  # noqa
            )
            self.search_gig_genres = " ".join(
                genre.genre for genre in self.gig.genres.all()  # noqa
            )
        # Saving here for fields to show up for SearchVector.
        super().save()
        self.search_vector = search.SearchVector(
            "search_username",
            "search_members",
            "search_gig_title",
            "search_gig_description",
            "search_gig_location",
            "search_gig_country",
            "search_gig_genres",
        )
        super().save()


class Message(BaseModel):
    """
    Note! if PUSH_NOTIFICATIONS_ENABLED is True a push notification is
    sent to other members of this message's room (not the creating user).
    This is done through a Django signal.
    """

    user = models.ForeignKey(
        "custom_user.User",
        on_delete=models.CASCADE,
        related_name="messages",
    )
    room = models.ForeignKey(
        "chat.Room",
        on_delete=models.CASCADE,
        related_name="messages",
    )
    message = models.TextField(default="")

    def save(self, *args, **kwargs):
        super().save()
        self.room.update_search_vector()
        if self.room.gig:
            self.room.gig.update_search_vector()
