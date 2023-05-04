# Generated by Django 4.1.2 on 2023-05-01 16:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("chat", "0002_room_remove_message_chat_delete_chat_message_room"),
    ]

    operations = [
        migrations.AddField(
            model_name="room",
            name="members",
            field=models.ManyToManyField(
                related_name="rooms_membership", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name="room",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="rooms_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]