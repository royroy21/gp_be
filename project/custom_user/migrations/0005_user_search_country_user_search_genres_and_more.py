# Generated by Django 4.1.2 on 2024-07-04 14:26

import django.contrib.postgres.search
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("custom_user", "0004_alter_user_room_ids_with_unread_messages"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="search_country",
            field=models.CharField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="search_genres",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="room_ids_with_unread_messages",
            field=models.JSONField(default=list),
        ),
    ]
