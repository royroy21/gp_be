import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthTestCase(TestCase):
    def setUp(self):
        username = "fred"
        password = "secret"
        self.user = User.objects.create_user(
            username,
            f"{username}@example.com",
            password,
        )
        self.drf_client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.drf_client.credentials(
            HTTP_AUTHORIZATION="JWT " + str(refresh.access_token),
        )

    def test_get_user_where_user_is_owner(self):
        response = self.drf_client.get(
            path=reverse("user-detail", args=(self.user.id,)),
        )
        expected_keys = ["id", "username", "email", "subscribed_to_emails"]
        self.assertEqual(sorted(response.data.keys()), sorted(expected_keys))
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(
            response.data["subscribed_to_emails"],
            self.user.subscribed_to_emails,
        )

    def test_get_user_where_user_is_not_owner(self):
        # email should not be present in expected keys
        username = "jiggy"
        password = "secret"
        user = User.objects.create_user(
            username,
            f"{username}@example.com",
            password,
        )
        drf_client = APIClient()
        refresh = RefreshToken.for_user(user)
        drf_client.credentials(
            HTTP_AUTHORIZATION="JWT " + str(refresh.access_token),
        )
        response = drf_client.get(
            path=reverse("user-detail", args=(self.user.id,)),
        )
        expected_keys = ["id", "username"]
        self.assertEqual(sorted(response.data.keys()), sorted(expected_keys))
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["username"], self.user.username)

    def test_get_user_where_user_is_unauthenticated(self):
        drf_client = APIClient()
        response = drf_client.get(
            path=reverse("user-detail", args=(self.user.id,)),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_user_where_user_is_owner(self):
        self.assertEqual(self.user.subscribed_to_emails, True)
        data = json.dumps(
            {
                "username": self.user.username,
                "subscribed_to_emails": False,
            }
        )
        response = self.drf_client.patch(
            path=reverse("user-detail", args=(self.user.id,)),
            data=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.subscribed_to_emails, False)

    def test_patch_user_where_user_is_not_owner(self):
        self.assertEqual(self.user.subscribed_to_emails, True)
        username = "jiggy"
        password = "secret"
        user = User.objects.create_user(
            username,
            f"{username}@example.com",
            password,
        )
        drf_client = APIClient()
        refresh = RefreshToken.for_user(user)
        drf_client.credentials(
            HTTP_AUTHORIZATION="JWT " + str(refresh.access_token),
        )
        data = json.dumps(
            {
                "username": self.user.username,
                "subscribed_to_emails": False,
            }
        )
        response = drf_client.patch(
            path=reverse("user-detail", args=(self.user.id,)),
            data=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.user.refresh_from_db()
        self.assertEqual(self.user.subscribed_to_emails, True)

    def test_patch_user_where_user_is_unauthenticated(self):
        self.assertEqual(self.user.subscribed_to_emails, True)
        drf_client = APIClient()
        data = json.dumps(
            {
                "username": self.user.username,
                "subscribed_to_emails": False,
            }
        )
        response = drf_client.patch(
            path=reverse("user-detail", args=(self.user.id,)),
            data=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.user.refresh_from_db()
        self.assertEqual(self.user.subscribed_to_emails, True)

    def test_create_user(self):
        drf_client = APIClient()
        username = "jinky"
        data = json.dumps(
            {
                "username": username,
                "subscribed_to_emails": True,
            }
        )
        response = drf_client.post(
            path=reverse("user-list"),
            data=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.filter(username=username).first()
        self.assertTrue(user)
        self.assertEqual(user.username, username)

    def test_list_users_where_user_is_authenticated(self):
        response = self.drf_client.get(
            path=reverse("user-list"),
        )
        expected_keys = ["id", "username"]
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            sorted(response.data[0].keys()),
            sorted(expected_keys),
        )
        self.assertEqual(response.data[0]["id"], self.user.id)
        self.assertEqual(response.data[0]["username"], self.user.username)

    def test_list_users_where_user_is_unauthenticated(self):
        drf_client = APIClient()
        response = drf_client.get(
            path=reverse("user-list"),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_me_endpoint_using_valid_user(self):
        response = self.drf_client.get(path=reverse("user-me"))
        expected_keys = ["id", "username", "email", "subscribed_to_emails"]
        self.assertEqual(sorted(response.data.keys()), sorted(expected_keys))
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(
            response.data["subscribed_to_emails"],
            self.user.subscribed_to_emails,
        )

    def test_me_endpoint_using_invalid_user(self):
        drf_client = APIClient()
        response = drf_client.get(path=reverse("user-me"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy(self):
        response = self.drf_client.delete(
            path=reverse("user-detail", args=(self.user.id,)),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
