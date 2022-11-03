import random

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt import serializers as simplejwt_serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "subscribed_to_emails",
        ]


class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    password = simplejwt_serializers.PasswordField(required=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
        ]

    def create_username(self):
        username = f"gigpig#{random.randint(1000, 999999)}"
        if username in User.objects.values_list("username", flat=True):
            return self.create_username()
        return username

    def create(self, validated_data):
        return User.objects.create_user(
            username=self.create_username(),
            **validated_data,
        )

    @property
    def data(self):
        tokens = RefreshToken.for_user(self.instance)
        return {
            "refresh": str(tokens),
            "access": str(tokens.access_token),
        }


class UserSerializerIfNotOwner(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
        ]
