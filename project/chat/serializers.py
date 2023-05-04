from rest_framework import serializers

from project.chat import models
from project.custom_user import serializers as user_serializers


class MessageSerializer(serializers.ModelSerializer):
    user = user_serializers.UserSerializerSimple(read_only=True)

    class Meta:
        model = models.Message
        fields = (
            "user",
            "content",
        )
