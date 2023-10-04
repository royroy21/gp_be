from django.db import models

from project.core.models import BaseModel


class Album(BaseModel):
    title = models.CharField(
        max_length=254,
        default="default",
    )

    DEFAULT_DESCRIPTION_FOR_GIG = "Default album for your gig."
    DEFAULT_DESCRIPTION_FOR_PROFILE = "Default album for your profile."
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

    @classmethod
    def create_default_album_for_gig(cls, gig, user):
        return cls.objects.create(
            description=cls.DEFAULT_DESCRIPTION_FOR_GIG,
            user=user,
            gig=gig,
        )

    @classmethod
    def create_default_album_for_profile(cls, profile, user):
        return cls.objects.create(
            description=cls.DEFAULT_DESCRIPTION_FOR_PROFILE,
            user=user,
            profile=profile,
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
