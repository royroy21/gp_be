import json
from datetime import timedelta

from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from project.audio import models as audio_models
from project.core import tests as core_tests
from project.country import models as country_models
from project.genre import models as genre_models
from project.gig import models


class GigAPITestCase(TestCase):
    def setUp(self):
        self.user, self.drf_client = core_tests.setup_user_with_drf_client(
            username="fred",
        )
        self.genre = genre_models.Genre.objects.create(genre="Doom")
        self.country = country_models.CountryCode.objects.create(
            country="United Kingdom",
            code="GB",
        )

        self.user_gig = models.Gig.objects.create(
            user=self.user,
            title="Man Feelings",
            location="Brixton academy",
            country=self.country,
            start_date=timezone.now() + timedelta(hours=1),
        )
        self.user_gig.genres.add(self.genre)

        self.other_gig = models.Gig.objects.create(
            user=core_tests.create_user(username="jiggy"),
            title="Man Feelings",
            location="Brixton academy",
            country=self.country,
            start_date=timezone.now() + timedelta(hours=1),
        )
        self.other_gig.genres.add(self.genre)

    def test_filter_out_user_gigs(self):
        # Gigs user created shouldn't be visible without the `my_gigs` flag
        response = self.drf_client.get(path=reverse("gig-api-list"))
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.other_gig.id),
        )

    def test_filter_with_my_gigs_flag(self):
        # Only gigs user created should be visible without the `my_gigs` flag
        response = self.drf_client.get(
            path=reverse("gig-api-list") + "?my_gigs=true",
        )
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.user_gig.id),
        )

    def test_out_of_date_gig(self):
        # Gigs that have already started should not be displayed
        gig = models.Gig.objects.create(
            user=core_tests.create_user(username="bungle"),
            title="Man Feelings",
            location="Brixton academy",
            country=self.country,
            start_date=timezone.now() - timedelta(hours=1),
        )
        gig.genres.add(self.genre)

        response = self.drf_client.get(path=reverse("gig-api-list"))
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.other_gig.id),
        )

    def test_create_gig(self):
        start_date = timezone.now() + timedelta(hours=1)
        data = {
            "title": "Secret Gillaband gig!",
            "location": "Camden",
            "country": {
                "code": self.country.code,
            },
            "genres": [{"id": str(self.genre.id), "genre": self.genre.genre}],
            "start_date": start_date.isoformat(),
        }
        response = self.drf_client.post(
            path=reverse("gig-api-list"),
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        gig_query = models.Gig.objects.filter(title=data["title"])
        self.assertEqual(gig_query.count(), 1)
        gig = gig_query.first()
        self.assertEqual(gig.user, self.user)
        self.assertEqual(gig.genres.count(), 1)
        self.assertEqual(gig.genres.first().genre, self.genre.genre)

        # Test default album is created
        album_query = audio_models.Album.objects.filter(
            title="default",
            gig=gig,
            user=self.user,
        )
        self.assertTrue(album_query.exists())

    def test_patch_gig(self):
        updated_title = "Secret Man Feelings gig!"
        updated_country = country_models.CountryCode.objects.create(
            country="Poland",
            code="PL",
        )
        updated_genre = self.genre = genre_models.Genre.objects.create(
            genre="Indie"
        )
        data = {
            "title": updated_title,
            "country": {"code": updated_country.code},
            "genres": [{"genre": updated_genre.genre}],
        }
        response = self.drf_client.patch(
            path=reverse("gig-api-detail", args=(self.user_gig.id,)),
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], updated_title)
        self.assertEqual(
            response.data["country"]["code"], updated_country.code
        )
        self.assertEqual(len(response.data["genres"]), 1)
        self.assertEqual(
            response.data["genres"][0]["genre"], updated_genre.genre
        )
        self.user_gig.refresh_from_db()
        self.assertEqual(self.user_gig.title, updated_title)
        self.assertEqual(self.user_gig.country, updated_country)
        self.assertEqual(self.user_gig.genres.first(), updated_genre)

    def test_update_gig_with_invalid_genres_data(self):
        # Checking if an ugly 500 isn't returned here.
        data = {
            "genres": [{"meow": True}],
        }
        response = self.drf_client.patch(
            path=reverse("gig-api-detail", args=(self.user_gig.id,)),
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("genres", response.data)

    def test_patch_gig_if_not_owner(self):
        _, drf_client = core_tests.setup_user_with_drf_client(
            username="bungle",
        )
        data = {
            "title": "Secret Man Feelings gig!",
        }
        response = drf_client.patch(
            path=reverse("gig-api-detail", args=(self.user_gig.id,)),
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_gigs_and_get_distance_from_user(self):
        self.user.point = Point(-0.0779528, 51.5131749)
        self.user.save()

        other_user = self.other_gig.user
        other_user.point = Point(-0.0780935, 51.5133267)
        other_user.save()

        response = self.drf_client.get(path=reverse("gig-api-list"))
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["user"]["distance_from_user"],
            "0.02 kilometers",
        )

    def test_search_vector(self):
        query = models.Gig.objects.filter(search_vector=self.user.username)
        self.assertTrue(query.exists())

        query = models.Gig.objects.filter(search_vector="blah blah blah")
        self.assertFalse(query.exists())
