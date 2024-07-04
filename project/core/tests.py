import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)
User = get_user_model()

AUTH_HEADER_NAME = settings.SIMPLE_JWT["AUTH_HEADER_NAME"]  # type: ignore
AUTH_HEADER_TYPE = settings.SIMPLE_JWT["AUTH_HEADER_TYPES"][0]  # type: ignore


def setup_user_with_drf_client(username, password="pa$$word"):
    """
    Creates a user for testing.
    Returns User object and authenticated DRF client.
    """
    user = create_user(username, password)
    refresh = RefreshToken.for_user(user)
    drf_client = APIClient()
    credentials = {
        AUTH_HEADER_NAME: f"{AUTH_HEADER_TYPE} {str(refresh.access_token)}"
    }
    drf_client.credentials(**credentials)
    return user, drf_client


def setup_user_with_jwt_headers(username, password="pa$$word", as_tuple=False):
    """
    Creates a user for testing.
    Returns User object and formatted http authorization header.
    """
    user = create_user(username, password)
    refresh = RefreshToken.for_user(user)
    token_value = f"{AUTH_HEADER_TYPE} {str(refresh.access_token)}"
    if as_tuple:
        auth_header = (AUTH_HEADER_NAME, token_value)
    else:
        auth_header = {
            AUTH_HEADER_NAME: token_value,
        }
    return user, auth_header


def create_user(username, password="pa$$word"):
    return User.objects.create_user(
        username,
        f"{username}@example.com",
        password,
    )
