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

    def __str__(self):
        return f"{self.type}, {self.user.get_username()}"


class Message(BaseModel):

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
    content = models.TextField(default="")

    def __str__(self):
        return f"for room:{self.room.id} {self.user.get_username()}"
