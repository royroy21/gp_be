from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt import serializers as simplejwt_serializers
from rest_framework_simplejwt.tokens import RefreshToken


class CustomTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = simplejwt_serializers.PasswordField()

    token_class = RefreshToken

    default_error_messages = {
        "no_active_account": _(
            "No active account found with the given credentials"
        )  # noqa
    }

    def validate_email(self, value):
        return value.lower()

    def validate(self, attrs):
        authenticate_kwargs = {
            "email": attrs["email"],
            "password": attrs["password"],
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)
        api_settings = simplejwt_serializers.api_settings

        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise simplejwt_serializers.exceptions.AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )

        refresh = self.get_token(self.user)

        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data

    @classmethod
    def get_token(cls, user):
        return cls.token_class.for_user(user)
