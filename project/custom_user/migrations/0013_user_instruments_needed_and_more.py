# Generated by Django 4.1.2 on 2024-08-13 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("instrument", "0001_initial"),
        ("custom_user", "0012_user_search_instruments"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="instruments_needed",
            field=models.ManyToManyField(
                blank=True,
                help_text="Instruments needed by band",
                related_name="instruments_needed_by_users",
                to="instrument.instrument",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="search_instruments_needed",
            field=models.TextField(null=True),
        ),
    ]
