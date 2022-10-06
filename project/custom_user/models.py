from django.contrib.auth import models as auth_models
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _


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

    def create_superuser(self, username, email, password, **extra_fields):
        return self._create_user(
            username,
            email,
            password,
            is_staff=True,
            is_superuser=True,
            **extra_fields,
        )


class User(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):

    objects = UserManager()

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
    first_name = models.CharField(max_length=254, default="")
    last_name = models.CharField(max_length=254, default="")
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    subscribed_to_emails = models.BooleanField(default=True)

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"

    def __str__(self):
        return f"{self.username}@{self.email}"
