import json

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from project.core.tests import setup_user, setup_user_with_drf_client
from project.country import models as country_models
from project.custom_user import serializers

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
        expected_keys = serializers.UserSerializer.Meta.fields
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
        expected_keys = serializers.UserSerializerMinimum.Meta.fields
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
        other_user, _ = setup_user_with_drf_client(
            username="mr_meow",
            password="pa$$word",
        )
        response = self.drf_client.get(
            path=reverse("user-list"),
        )
        expected_keys = serializers.UserSerializerMinimum.Meta.fields
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            sorted(response.data["results"][0].keys()),
            sorted(expected_keys),
        )
        self.assertEqual(response.data["results"][0]["id"], other_user.id)
        self.assertEqual(
            response.data["results"][0]["username"],
            other_user.username,
        )

    def test_list_users_where_user_is_unauthenticated(self):
        drf_client = APIClient()
        response = drf_client.get(
            path=reverse("user-list"),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_me_endpoint_using_valid_user(self):
        response = self.drf_client.get(path=reverse("user-me"))
        expected_keys = serializers.UserSerializer.Meta.fields
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

    def test_list_users_and_get_distance_from_user(self):
        self.user.location = Point(-0.0779528, 51.5131749)
        self.user.save()

        other_user, _ = setup_user_with_drf_client(
            username="mr_meow",
            password="pa$$word",
        )
        other_user.location = Point(-0.0780935, 51.5133267)
        other_user.save()

        response = self.drf_client.get(path=reverse("user-list"))
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["distance_from_user"],
            "0.02 kilometers",
        )

    def test_preferred_units(self):
        self.user.location = Point(-0.0779528, 51.5131749)
        self.user.preferred_units = User.MILES
        self.user.save()

        other_user, _ = setup_user_with_drf_client(
            username="mr_meow",
            password="pa$$word",
        )
        other_user.location = Point(-0.0780935, 51.5133267)
        other_user.save()

        response = self.drf_client.get(path=reverse("user-list"))
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["distance_from_user"],
            "0.01 miles",
        )


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
        serializer = serializers.UserSerializer(
            self.user,
            data=location,
            partial=True,
        )
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.location.coords, (longitude, latitude))
        self.assertEqual(self.user.country, country)

    def test_update_country_check_units_update_to_miles(self):
        country = country_models.CountryCode.objects.create(
            country="United Kingdom",
            code="GB",
        )
        data = {"country": {"code": country.code}}
        serializer = serializers.UserSerializer(
            self.user,
            data=data,
            partial=True,
        )
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.units, User.MILES)

    def test_update_country_check_units_update_to_kilometers(self):
        country = country_models.CountryCode.objects.create(
            country="France",
            code="FR",
        )
        data = {"country": {"code": country.code}}
        serializer = serializers.UserSerializer(
            self.user,
            data=data,
            partial=True,
        )
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.units, User.KM)
