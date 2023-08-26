from django.contrib.auth import models as auth_models
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.core.validators import EmailValidator
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework_simplejwt import tokens

from project.core.models import BaseModel


class UserManager(auth_models.BaseUserManager):
    def _create_user(
        self,
        username,
        email,
        password=None,
        is_staff=False,
        is_superuser=False,
        **extra_fields,
    ):
        now = timezone.now()
        user = self.model(
            username=username.strip(),
            email=email.lower().strip(),
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields,
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        return self._create_user(
            username,
            email,
            password,
            is_staff=False,
            is_superuser=False,
            **extra_fields,
        )

    def create_superuser(
        self,
        username,
        email=None,
        password=None,
        **extra_fields,
    ):
        if not email:
            email = username + "@example.com"
        return self._create_user(
            username,
            email,
            password,
            is_staff=True,
            is_superuser=True,
            **extra_fields,
        )


class User(  # type: ignore
    auth_models.AbstractBaseUser,
    auth_models.PermissionsMixin,
):

    objects = UserManager()
    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"

    username = models.CharField(
        max_length=254,
        unique=True,
        error_messages={
            "unique": _("Sorry! Username already exists."),
        },
    )
    email = models.CharField(
        max_length=254,
        unique=True,
        validators=[EmailValidator()],
        error_messages={
            "unique": _("Sorry! Email address already exists."),
        },
        default="",
    )
    first_name = models.CharField(max_length=254, default="", blank=True)
    last_name = models.CharField(max_length=254, default="", blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    subscribed_to_emails = models.BooleanField(default=True)
    location = models.PointField(default=Point([]))
    country = models.ForeignKey(
        "country.CountryCode",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="users",
    )
    favorite_users = models.ManyToManyField("User")

    # Personal
    bio = models.TextField(default="", blank=True)
    genres = models.ManyToManyField(
        "genre.Genre",
        blank=True,
        related_name="users",
    )

    # Preferences
    DARK = "dark"
    LIGHT = "light"
    THEME_CHOICES = [
        (DARK, DARK),
        (LIGHT, LIGHT),
    ]
    theme = models.CharField(
        max_length=254,
        default=DARK,
        choices=THEME_CHOICES,
    )
    KM = "kilometers"
    MILES = "miles"
    UNIT_CHOICES = [
        (KM, KM),
        (MILES, MILES),
    ]
    units = models.CharField(
        max_length=254,
        default=KM,
        choices=UNIT_CHOICES,
    )
    preferred_units = models.CharField(
        max_length=254,
        default=None,
        blank=True,
        null=True,
        choices=UNIT_CHOICES,
    )
    image = models.ImageField(
        upload_to="user",
        blank=True,
        null=True,
    )
    thumbnail = models.ImageField(
        upload_to="user",
        blank=True,
        null=True,
    )

    def get_jwt(self):
        refresh = tokens.RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    @property
    def genres_indexing(self):
        """Used in Elasticsearch indexing."""
        return [genre.genre for genre in self.genres.filter(active=True)]


class NotificationToken(BaseModel):
    """
    Token used for using push notifications.
    """

    user = models.ForeignKey(
        "custom_user.User",
        on_delete=models.CASCADE,
        related_name="notification_tokens",
    )
    token = models.CharField(max_length=254)
