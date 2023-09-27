# Generated by Django 4.1.2 on 2023-09-26 13:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("gig", "0010_gig_thumbnail"),
    ]

    operations = [
        migrations.CreateModel(
            name="Album",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_updated", models.DateTimeField(auto_now=True)),
                ("active", models.BooleanField(default=True)),
                ("title", models.CharField(default="default", max_length=254)),
                ("description", models.TextField(blank=True, default="")),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="audio_images"
                    ),
                ),
                (
                    "gig",
                    models.ForeignKey(
                        blank=True,
                        help_text=(
                            "Gig this album is linked to. This "
                            "maybe empty if linked to a profile."
                        ),
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="gig.gig",
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        blank=True,
                        help_text=(
                            "Profile this album is linked to. "
                            "This maybe empty if linked to a gig."
                        ),
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="albums",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Audio",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_updated", models.DateTimeField(auto_now=True)),
                ("active", models.BooleanField(default=True)),
                ("title", models.CharField(max_length=254)),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="audio_images"
                    ),
                ),
                ("file", models.FileField(upload_to="audio_files")),
                (
                    "album",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="audio_tracks",
                        to="audio.album",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="audio_files",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
