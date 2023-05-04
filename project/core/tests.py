import functools
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from elasticsearch.exceptions import ConnectionError
from elasticsearch_dsl import connections
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from project.core.console import print_error_to_console

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


def with_elasticsearch(func):
    """
    This deletes elasticsearch indices for a test
    so to isolate elasticsearch data between tests.
    """

    @functools.wraps(func)
    def wrap(*args, **kwargs):
        try:
            # Tearing down before test so to clear
            # elasticsearch if a test beforehand errors.
            teardown_elasticsearch()
            func(*args, **kwargs)
            teardown_elasticsearch()
        except ConnectionError:
            print_error_to_console(
                f"Could not run test `{func.__name__}` "
                f"waiting for elasticsearch to start. "
                f"To avoid this error please start the "
                f"elasticsearch server before running tests.\n"
            )

    return wrap


def teardown_elasticsearch():
    elasticsearch_connection = connections.get_connection()
    for index_name in settings.ELASTICSEARCH_INDEX_NAMES.values():
        elasticsearch_connection.indices.delete(index=index_name, ignore=404)
