# Generated by Django 4.1.2 on 2023-02-13 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gig", "0002_genre_active_gig_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="genre",
            name="rank",
            field=models.IntegerField(default=1),
        ),
    ]
