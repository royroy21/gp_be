# Generated by Django 4.1.2 on 2023-08-01 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gig", "0008_delete_genre_alter_gig_genres"),
    ]

    operations = [
        migrations.AddField(
            model_name="gig",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="gig"),
        ),
    ]