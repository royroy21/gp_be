import random

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt import serializers as simplejwt_serializers
from rest_framework_simplejwt.tokens import RefreshToken

from project.country import serializers as country_serializers
from project.location.fields import LocationField
from project.location.helpers import get_distance_between_points

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    location = LocationField()
    country = country_serializers.CountrySerializer()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "subscribed_to_emails",
            "location",
            "country",
            "theme",
        ]


class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(
                message="Account with this email already exists.",
                queryset=User.objects.all(),
            )
        ],
    )
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


class UserSerializerMinimum(serializers.ModelSerializer):
    distance_from_user = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "distance_from_user",
        ]

    def get_distance_from_user(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            if user.location and obj.location:
                distance = get_distance_between_points(
                    point_1=user.location,
                    point_2=obj.location,
                    units=user.units,
                )
                return f"{distance} {user.units}"

        return None
