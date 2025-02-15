import uuid

from django.contrib.auth import models as auth_models
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.postgres import search
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    point = models.PointField(default=Point([]), blank=True)
    location = models.CharField(
        max_length=254,
        help_text="Town or city",
        default=str,
    )
    country = models.ForeignKey(
        "country.CountryCode",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="users",
    )
    favorite_users = models.ManyToManyField("User")
    favorite_gigs = models.ManyToManyField(
        "gig.Gig",
        related_name="favourite_for_users",
    )

    # Personal
    bio = models.TextField(default="", blank=True)
    genres = models.ManyToManyField(
        "genre.Genre",
        blank=True,
        related_name="users",
    )
    instruments = models.ManyToManyField(
        "instrument.Instrument",
        blank=True,
        related_name="users",
    )
    instruments_needed = models.ManyToManyField(
        "instrument.Instrument",
        blank=True,
        related_name="instruments_needed_by_users",
        help_text="Instruments needed by band",
    )
    is_band = models.BooleanField(default=False)
    is_musician = models.BooleanField(default=False)
    is_looking_for_musicians = models.BooleanField(default=False)
    is_looking_for_band = models.BooleanField(default=False)

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
    room_ids_with_unread_messages = models.JSONField(default=list)

    search_country = models.CharField(max_length=254, null=True)
    search_genres = models.TextField(null=True)
    search_instruments = models.TextField(null=True)
    search_instruments_needed = models.TextField(null=True)
    search_vector = search.SearchVectorField(null=True)

    def save(self, *args, **kwargs):
        super().save()
        self.update_search_vector()
        for gig in self.gigs.filter(active=True):  # noqa
            gig.update_search_vector()

    def update_search_vector(self):
        if self.country:
            self.search_country = (
                f"{self.country.country} {self.country.code}"  # noqa
            )
        self.search_genres = " ".join(
            genre.genre for genre in self.genres.all()
        )
        if self.is_musician:
            self.search_instruments = " ".join(
                instrument.instrument for instrument in self.instruments.all()
            )
        if self.is_band:
            self.search_instruments_needed = " ".join(
                instrument.instrument
                for instrument in self.instruments_needed.all()
            )
        # Saving here for fields to show up for SearchVector.
        super().save()
        self.search_vector = search.SearchVector(
            "username",
            "location",
            "search_country",
            "search_genres",
            "search_instruments",
            "search_instruments_needed",
        )
        super().save()

    def get_jwt(self):
        refresh = tokens.RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def number_of_active_gigs(self):
        return (
            self.gigs.filter(active=True)  # noqa
            .exclude(
                start_date__lte=timezone.now(),
            )
            .count()
        )

    def add_room_id_with_unread_messages(self, new_room_id):
        room_ids = self.room_ids_with_unread_messages
        if new_room_id in room_ids:
            return

        room_ids.append(new_room_id)
        self.room_ids_with_unread_messages = room_ids
        self.save()


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


class ResetPasswordToken(BaseModel):
    user = models.ForeignKey(
        "custom_user.User",
        on_delete=models.CASCADE,
        related_name="reset_password_tokens",
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False)
