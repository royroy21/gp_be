# Generated by Django 4.1.2 on 2024-08-13 09:06

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Instrument",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_updated", models.DateTimeField(auto_now=True)),
                ("active", models.BooleanField(default=True)),
                ("instrument", models.CharField(max_length=254, unique=True)),
                ("rank", models.IntegerField(default=1)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
