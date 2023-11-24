# Generated by Django 4.1.2 on 2023-11-24 11:23

import uuid

import django.contrib.gis.db.models.fields
import django.contrib.gis.geos.point
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("country", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "password",
                    models.CharField(max_length=128, verbose_name="password"),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "Sorry! Username already exists."
                        },
                        max_length=254,
                        unique=True,
                    ),
                ),
                (
                    "email",
                    models.CharField(
                        default="",
                        error_messages={
                            "unique": "Sorry! Email address already exists."
                        },
                        max_length=254,
                        unique=True,
                        validators=[django.core.validators.EmailValidator()],
                    ),
                ),
                (
                    "first_name",
                    models.CharField(blank=True, default="", max_length=254),
                ),
                (
                    "last_name",
                    models.CharField(blank=True, default="", max_length=254),
                ),
                ("is_staff", models.BooleanField(default=False)),
                ("is_superuser", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("last_login", models.DateTimeField(blank=True, null=True)),
                ("date_joined", models.DateTimeField(auto_now_add=True)),
                ("subscribed_to_emails", models.BooleanField(default=True)),
                (
                    "location",
                    django.contrib.gis.db.models.fields.PointField(
                        default=django.contrib.gis.geos.point.Point([]),
                        srid=4326,
                    ),
                ),
                ("bio", models.TextField(blank=True, default="")),
                (
                    "theme",
                    models.CharField(
                        choices=[("dark", "dark"), ("light", "light")],
                        default="dark",
                        max_length=254,
                    ),
                ),
                (
                    "units",
                    models.CharField(
                        choices=[
                            ("kilometers", "kilometers"),
                            ("miles", "miles"),
                        ],
                        default="kilometers",
                        max_length=254,
                    ),
                ),
                (
                    "preferred_units",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("kilometers", "kilometers"),
                            ("miles", "miles"),
                        ],
                        default=None,
                        max_length=254,
                        null=True,
                    ),
                ),
                (
                    "image",
                    models.ImageField(blank=True, null=True, upload_to="user"),
                ),
                (
                    "thumbnail",
                    models.ImageField(blank=True, null=True, upload_to="user"),
                ),
                (
                    "country",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="users",
                        to="country.countrycode",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="NotificationToken",
            fields=[
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_updated", models.DateTimeField(auto_now=True)),
                ("active", models.BooleanField(default=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("token", models.CharField(max_length=254)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification_tokens",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
