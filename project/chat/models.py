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

    def members_indexing(self):
        """Used in Elasticsearch indexing."""
        return list(
            self.members.filter(is_active=True).values_list(
                "username",
                flat=True,
            )
        )

    def gig_indexing(self):
        """Used in Elasticsearch indexing."""
        if not self.gig:
            return None

        genres = " ".join(
            list(
                self.gig.genres.filter(active=True).values_list(  # noqa
                    "genre",
                    flat=True,
                )
            )
        )
        # Putting all gig data into a string for search purposes.
        return (
            f"{self.gig.title} "  # noqa
            f"{self.gig.description} "  # noqa
            f"{self.gig.location} {genres}"  # noqa
        )

    def last_message_date_indexing(self):
        """Used in Elasticsearch indexing."""
        if not self.messages.exists():  # noqa
            return None

        return (
            self.messages.all().order_by("date_created").last().date_created
        )  # noqa

    def has_messages_indexing(self):
        """Used in Elasticsearch indexing."""
        return self.messages.exists()  # noqa


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
