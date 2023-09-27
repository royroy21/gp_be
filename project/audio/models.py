from django.db import models

from project.core.models import BaseModel


class Album(BaseModel):
    title = models.CharField(
        max_length=254,
        default="default",
    )
    description = models.TextField(
        default="",
        blank=True,
    )
    genres = models.ManyToManyField(
        "genre.Genre",
        blank=True,
        related_name="albums",
    )
    image = models.ImageField(
        upload_to="album_images",
        blank=True,
        null=True,
    )
    thumbnail = models.ImageField(
        upload_to="album_thumbnails",
        blank=True,
        null=True,
    )
    profile = models.ForeignKey(
        "custom_user.User",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text=(
            "Profile this album is linked to. "
            "This maybe empty if linked to a gig."
        ),
    )
    gig = models.ForeignKey(
        "gig.Gig",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text=(
            "Gig this album is linked to. "
            "This maybe empty if linked to a profile."
        ),
    )
    user = models.ForeignKey(
        "custom_user.User",
        on_delete=models.CASCADE,
        related_name="albums",
    )


class Audio(BaseModel):
    title = models.CharField(
        max_length=254,
    )
    position = models.IntegerField(
        help_text="position in album",
    )
    image = models.ImageField(
        upload_to="audio_images",
        blank=True,
        null=True,
    )
    thumbnail = models.ImageField(
        upload_to="audio_thumbnails",
        blank=True,
        null=True,
    )
    file = models.FileField(
        upload_to="audio_files",
        blank=True,
        null=True,
    )
    album = models.ForeignKey(
        "audio.Album",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="audio_tracks",
    )
    user = models.ForeignKey(
        "custom_user.User",
        on_delete=models.CASCADE,
        related_name="audio_files",
    )
