# Generated by Django 4.1.2 on 2022-12-20 15:25

import django.contrib.gis.db.models.fields
import django.contrib.gis.geos.point
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("custom_user", "0002_alter_user_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="location",
            field=django.contrib.gis.db.models.fields.PointField(
                default=django.contrib.gis.geos.point.Point([]), srid=4326
            ),
        ),
    ]