# Generated by Django 4.1.2 on 2024-08-13 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("custom_user", "0009_rename_location_user_point"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="location",
            field=models.CharField(
                default=str, help_text="Town or city", max_length=254
            ),
        ),
    ]
