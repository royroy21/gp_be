# Generated by Django 4.1.2 on 2024-08-13 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("instrument", "0001_initial"),
        ("custom_user", "0007_resetpasswordtoken"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="instruments",
            field=models.ManyToManyField(
                blank=True, related_name="users", to="instrument.instrument"
            ),
        ),
    ]
