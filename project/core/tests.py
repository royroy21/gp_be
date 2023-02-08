from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def setup_user_with_drf_client(username, password):
    user = setup_user(username, password)
    refresh = RefreshToken.for_user(user)
    drf_client = APIClient()
    drf_client.credentials(
        HTTP_AUTHORIZATION="JWT " + str(refresh.access_token),
    )
    return user, drf_client


def setup_user(username, password):
    return User.objects.create_user(
        username,
        f"{username}@example.com",
        password,
    )
