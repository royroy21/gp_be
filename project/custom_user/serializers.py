import random

from django.contrib.auth import get_user_model
from django.core import exceptions as django_exceptions
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt import serializers as simplejwt_serializers
from rest_framework_simplejwt.tokens import RefreshToken

from project.audio import models as audio_models
from project.country import serializers as country_serializers
from project.custom_user import models
from project.genre import serializers as genre_serializers
from project.image import tasks as image_tasks
from project.location.fields import LocationField
from project.location.helpers import get_distance_between_points
from project.site import domain

User = get_user_model()


COUNTRIES_THAT_USE_MILES = [
    "GB",
    "US",
]


class UserSerializer(serializers.ModelSerializer):
    location = LocationField()
    country = country_serializers.CountrySerializer()
    genres = genre_serializers.GenreSerializer(many=True)
    number_of_active_gigs = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False, allow_null=True)
    thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "subscribed_to_emails",
            "location",
            "country",
            "bio",
            "genres",
            "theme",
            "units",
            "preferred_units",
            "number_of_active_gigs",
            "image",
            "thumbnail",
        ]

    def get_units(self, country):
        if country.code in COUNTRIES_THAT_USE_MILES:
            return User.MILES  # noqa
        else:
            return User.KM  # noqa

    def update(self, instance, validated_data):
        copy_of_validated_data = self.copy_data(validated_data)
        genres = copy_of_validated_data.pop("genres", None)
        user = super().update(instance, copy_of_validated_data)
        if genres is not None:
            user.genres.clear()
            user.genres.add(*genres)
        if copy_of_validated_data.get("image", None) is not None:
            image_tasks.create_thumbnail.delay("custom_user", "user", user.id)
        return user

    def copy_data(self, data):
        # Copying like this as deepcopy doesn't like in memory files.
        data_copy = {
            key: value for key, value in data.items() if key != "image"
        }
        if "country" in data_copy:
            data_copy["units"] = self.get_units(data_copy["country"])

        if "image" in data:
            # Adding like this as we need to preserve None for
            # images as this indicates an image to be removed.
            data_copy["image"] = data["image"]
            # Removing thumbnail here as the
            # create_gig_thumbnail task will update it.
            # Or if image is deleted also delete thumbnail.
            data_copy["thumbnail"] = None

        return data_copy

    def get_number_of_active_gigs(self, instance):
        return instance.number_of_active_gigs()


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
        user = User.objects.create_user(
            username=self.create_username(),
            **validated_data,
        )
        audio_models.Album.create_default_album_for_profile(
            profile=user,
            user=user,
        )
        return user

    @property
    def data(self):
        tokens = RefreshToken.for_user(self.instance)
        return {
            "refresh": str(tokens),
            "access": str(tokens.access_token),
        }


user_non_sensitive_fields = [
    field
    for field in UserSerializer.Meta.fields
    if field
    not in [
        "email",
        "subscribed_to_emails",
        "location",
        "theme",
        "units",
        "preferred_units",
    ]
]


class UserSerializerIfNotOwner(serializers.ModelSerializer):
    genres = serializers.SerializerMethodField()
    distance_from_user = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    country = country_serializers.CountrySerializer()

    class Meta:
        model = User
        fields = [
            "distance_from_user",
            "is_favorite",
        ] + user_non_sensitive_fields

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

    def get_genres(self, instance):
        """
        Genres returned like this,
        so we can pass the context object.
        """
        return genre_serializers.GenreSerializer(
            instance.genres.filter(active=True),
            many=True,
            read_only=True,
            context=self.context["request"],
        ).data

    def get_is_favorite(self, instance):
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        return user.favorite_users.filter(id=instance.id).exists()

    def get_image(self, instance):
        """
        Created URLs this way as sometimes when called this
        it doesn't have access to the request object or is
        using the SudoRequest object which doesn't have access
        to build_absolute_uri.
        """
        if not instance.image:
            return None
        return domain.build_absolute_uri(instance.image.url)

    def get_thumbnail(self, instance):
        """
        Created URLs this way as sometimes when called this
        it doesn't have access to the request object or is
        using the SudoRequest object which doesn't have access
        to build_absolute_uri.
        """
        if not instance.thumbnail:
            return None
        return domain.build_absolute_uri(instance.thumbnail.url)


class UserSerializerWithSimplifiedToInternalValue(UserSerializerIfNotOwner):
    """
    Used in other serializers to get the user object.
    """

    def to_internal_value(self, data):
        try:
            return models.User.objects.get(id=data.get("id"))
        except models.User.DoesNotExist:
            raise serializers.ValidationError({"User does not exist"})
        except django_exceptions.FieldError:
            raise serializers.ValidationError("Invalid data")
