from rest_framework import serializers

from project.gig import models


class GigSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Gig
        fields = [
            "id",
            "title",
            "venue",
            "location",
            "description",
            "genre",
            "start_date",
            "end_date",
        ]
