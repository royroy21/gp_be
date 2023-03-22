import random
from copy import deepcopy

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt import serializers as simplejwt_serializers
from rest_framework_simplejwt.tokens import RefreshToken

from project.country import serializers as country_serializers
from project.location.fields import LocationField
from project.location.helpers import get_distance_between_points

User = get_user_model()


COUNTRIES_THAT_USE_MILES = [
    "GB",
    "US",
]


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
            "units",
            "preferred_units",
        ]

    def get_units(self, country):
        if country.code in COUNTRIES_THAT_USE_MILES:
            return User.MILES
        else:
            return User.KM

    def update(self, instance, validated_data):
        copy_of_validated_data = deepcopy(validated_data)
        if "country" in copy_of_validated_data:
            copy_of_validated_data["units"] = self.get_units(
                copy_of_validated_data["country"]
            )
        return super().update(instance, copy_of_validated_data)


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
                units = user.preferred_units or user.units
                distance = get_distance_between_points(
                    point_1=user.location,
                    point_2=obj.location,
                    units=units,
                )
                return f"{distance} {units}"

        return None
