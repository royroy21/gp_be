# Generated by Django 4.1.2 on 2023-08-26 14:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("custom_user", "0012_user_image_user_thumbnail"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="favorite_users",
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]