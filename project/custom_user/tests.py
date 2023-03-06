import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from project.core.tests import setup_user, setup_user_with_drf_client
from project.country import models as country_models
from project.custom_user.serializers import UserSerializer

User = get_user_model()


class AuthTestCase(TestCase):
    def setUp(self):
        self.user, self.drf_client = setup_user_with_drf_client(
            username="fred",
            password="pa$$word",
        )

    def test_get_user_where_user_is_owner(self):
        response = self.drf_client.get(
            path=reverse("user-detail", args=(self.user.id,)),
        )
        expected_keys = [
            "id",
            "username",
            "email",
            "subscribed_to_emails",
            "location",
            "country",
        ]
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
        user, drf_client = setup_user_with_drf_client(
            username="jiggy",
            password="pa$$word",
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
        user, drf_client = setup_user_with_drf_client(
            username="jiggy",
            password="pa$$word",
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
        email = "jinky@example.com"
        password = "cats"
        data = json.dumps(
            {
                "email": email,
                "password": password,
                "subscribed_to_emails": True,
            }
        )
        response = drf_client.post(
            path=reverse("user-list"),
            data=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.filter(email=email).first()
        self.assertTrue(user)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

        # Check tokens return can be used to get user details
        drf_client = APIClient()
        drf_client.credentials(
            HTTP_AUTHORIZATION="JWT " + str(response.data["access"]),
        )
        response = drf_client.get(path=reverse("user-me"))
        self.assertEqual(response.data["email"], email)

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
        expected_keys = [
            "id",
            "username",
            "email",
            "subscribed_to_emails",
            "location",
            "country",
        ]
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

    def test_update_location(self):
        country = country_models.CountryCode.objects.create(
            country="United Kingdom",
            code="GB",
        )
        latitude = 51.513833
        longitude = -0.0764861
        data = json.dumps(
            {
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "country": {
                    "code": "GB",
                },
            }
        )
        response = self.drf_client.put(
            path=reverse("user-detail", args=(self.user.id,)),
            data=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.location.coords, (longitude, latitude))
        self.assertEqual(self.user.country, country)


class UserSerializerTestCase(TestCase):
    def setUp(self):
        self.user = setup_user(username="fred", password="pa$$word")

    def test_update_location(self):
        country = country_models.CountryCode.objects.create(
            country="United Kingdom",
            code="GB",
        )
        latitude = 51.513833
        longitude = -0.0764861
        location = {
            "location": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "country": {
                "code": "GB",
            },
        }
        serializer = UserSerializer(
            self.user,
            data=location,
            partial=True,
        )
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.location.coords, (longitude, latitude))
        self.assertEqual(self.user.country, country)
