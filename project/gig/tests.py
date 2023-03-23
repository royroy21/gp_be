import json
from datetime import timedelta

from django.contrib.gis.geos import Point
from django.db.models import signals
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

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

        # Disables django_elasticsearch_dsl signals for updating documents.
        signals.post_save.receivers = []

        self.user_gig = models.Gig.objects.create(
            user=self.user,
            title="Man Feelings",
            location="Brixton academy",
            country=self.country,
            start_date=timezone.now() + timedelta(hours=1),
        )
        self.user_gig.genres.add(self.genre)

        self.other_gig = models.Gig.objects.create(
            user=core_tests.setup_user(username="jiggy"),
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
        self.assertEqual(response.data["results"][0]["id"], self.other_gig.id)

    def test_filter_with_my_gigs_flag(self):
        # Only gigs user created should be visible without the `my_gigs` flag
        response = self.drf_client.get(
            path=reverse("gig-api-list") + "?my_gigs=true",
        )
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.user_gig.id)

    def test_out_of_date_gig(self):
        # Gigs that have already started should not be displayed
        gig = models.Gig.objects.create(
            user=core_tests.setup_user(username="bungle"),
            title="Man Feelings",
            location="Brixton academy",
            country=self.country,
            start_date=timezone.now() - timedelta(hours=1),
        )
        gig.genres.add(self.genre)

        response = self.drf_client.get(path=reverse("gig-api-list"))
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.other_gig.id)

    def test_create_gig(self):
        start_date = timezone.now() + timedelta(hours=1)
        data = {
            "title": "Secret Gillaband gig!",
            "location": "Camden",
            "country": {
                "code": self.country.code,
            },
            "genres": [{"id": self.genre.id, "genre": self.genre.genre}],
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
        self.assertIn("non_field_errors", response.data)

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
        self.user.location = Point(-0.0779528, 51.5131749)
        self.user.save()

        other_user = self.other_gig.user
        other_user.location = Point(-0.0780935, 51.5133267)
        other_user.save()

        response = self.drf_client.get(path=reverse("gig-api-list"))
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["user"]["distance_from_user"],
            "0.02 kilometers",
        )


class GigElasticSearchAPITestCase(TestCase):
    def setUp(self):
        self.user, self.drf_client = core_tests.setup_user_with_drf_client(
            username="fred",
        )
        self.genre = genre_models.Genre.objects.create(genre="Doom")
        self.default_country = country_models.CountryCode.objects.create(
            country="United Kingdom",
            code="GB",
        )

    def create_gig(
        self,
        user=None,
        title=None,
        location=None,
        country=None,
        genres=None,
        has_spare_ticket=False,
        start_date=None,
        end_date=None,
    ):
        gig = models.Gig.objects.create(
            user=user or self.user,
            title=title or "Man Feelings",
            location=location or "Brixton Academy",
            country=country or self.default_country,
            has_spare_ticket=has_spare_ticket,
            start_date=start_date or timezone.now() + timedelta(hours=1),
            end_date=end_date,
        )
        if genres:
            gig.genres.add(genres)
        else:
            gig.genres.add(self.genre)

        return gig

    @core_tests.with_elasticsearch
    def test_search_for_own_gig(self):
        # User created gigs should not appear in their searches.
        self.create_gig()
        response = self.drf_client.get(
            path=reverse("gig-search-list") + "?search=doo",
        )
        self.assertEqual(len(response.data["results"]), 0)

    @core_tests.with_elasticsearch
    def test_search_for_gig_by_username(self):
        # This should hit by providing the exact username
        username = "jiggy"
        gig = self.create_gig(user=core_tests.setup_user(username=username))
        response = self.drf_client.get(
            path=reverse("gig-search-list") + f"?search={username}",
        )
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], gig.id)
        self.assertEqual(
            response.data["results"][0]["user"]["username"],
            username,
        )

    @core_tests.with_elasticsearch
    def test_search_for_gig_by_providing_incomplete_username(self):
        # This should not hit as only providing exact usernames should work.
        username = "jiggy"
        self.create_gig(user=core_tests.setup_user(username=username))
        response = self.drf_client.get(
            path=reverse("gig-search-list") + f"?search={username[:3]}",
        )
        self.assertEqual(len(response.data["results"]), 0)

    @core_tests.with_elasticsearch
    def test_search_on_title(self):
        self.create_gig(user=core_tests.setup_user(username="jiggy"))
        search_term = "feelings"
        response = self.drf_client.get(
            path=reverse("gig-search-list") + f"?search={search_term}",
        )
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn(
            search_term,
            response.data["results"][0]["title"].lower(),
        )

    @core_tests.with_elasticsearch
    def test_search_on_genre(self):
        self.create_gig(user=core_tests.setup_user(username="jiggy"))
        search_term = "doom"
        response = self.drf_client.get(
            path=reverse("gig-search-list") + f"?search={search_term}",
        )
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn(
            search_term,
            response.data["results"][0]["genres"][0]["genre"].lower(),
        )

    @core_tests.with_elasticsearch
    def test_fuzzy_search_on_genre(self):
        self.create_gig(user=core_tests.setup_user(username="jiggy"))
        search_term = "dom"
        response = self.drf_client.get(
            path=reverse("gig-search-list") + f"?search={search_term}",
        )
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn(
            self.genre.genre.lower(),
            response.data["results"][0]["genres"][0]["genre"].lower(),
        )

    @core_tests.with_elasticsearch
    def test_search_for_out_of_date_gig(self):
        # This should not hit. Only gigs in the future should hit.
        self.create_gig(
            user=core_tests.setup_user(username="jiggy"),
            start_date=timezone.now() - timedelta(hours=1),
        )
        response = self.drf_client.get(
            path=reverse("gig-search-list") + "?search=doom",
        )
        self.assertEqual(len(response.data["results"]), 0)

    @core_tests.with_elasticsearch
    def test_search_on_location(self):
        self.create_gig(
            user=core_tests.setup_user(username="jiggy"),
        )
        search_term = "brixton"
        response = self.drf_client.get(
            path=reverse("gig-search-list") + f"?search={search_term}",
        )
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn(
            search_term,
            response.data["results"][0]["location"].lower(),
        )

    @core_tests.with_elasticsearch
    def test_search_on_has_spare_ticket(self):
        user = core_tests.setup_user(username="jiggy")
        gig = self.create_gig(
            user=user,
            has_spare_ticket=True,
        )
        self.create_gig(
            user=user,
        )
        response = self.drf_client.get(
            path=reverse("gig-search-list") + "?has_spare_ticket=true",
        )
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], gig.id)

    @core_tests.with_elasticsearch
    def test_search_on_start_date(self):
        user = core_tests.setup_user(username="jiggy")
        self.create_gig(
            user=user,
            start_date=timezone.now() + timedelta(days=1),
        )
        self.create_gig(
            user=user,
            start_date=timezone.now() + timedelta(days=2),
        )
        gig = self.create_gig(
            user=user,
            start_date=timezone.now() + timedelta(days=5),
        )
        date = timezone.now() + timedelta(days=4)
        response = self.drf_client.get(
            path=(
                reverse("gig-search-list")
                + f"?start_date__gt={date.date().isoformat()}"
            ),
        )
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], gig.id)

    @core_tests.with_elasticsearch
    def test_order_by_start_date(self):
        user = core_tests.setup_user(username="jiggy")
        gig_second = self.create_gig(
            user=user, start_date=timezone.now() + timedelta(days=5)
        )
        gig_first = self.create_gig(
            user=user, start_date=timezone.now() + timedelta(days=4)
        )
        gig_last = self.create_gig(
            user=user, start_date=timezone.now() + timedelta(days=6)
        )
        response = self.drf_client.get(
            path=reverse("gig-search-list") + "?order_by=start_date",
        )
        self.assertEqual(len(response.data["results"]), 3)
        self.assertEqual(response.data["results"][0]["id"], gig_first.id)
        self.assertEqual(response.data["results"][1]["id"], gig_second.id)
        self.assertEqual(response.data["results"][2]["id"], gig_last.id)

    @core_tests.with_elasticsearch
    def test_filter_by_my_gigs(self):
        other_user = core_tests.setup_user(username="jiggy")
        self.create_gig(user=other_user)
        my_gig = self.create_gig()
        response = self.drf_client.get(
            path=reverse("gig-search-list") + "?my_gigs=true",
        )
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], my_gig.id)

    @core_tests.with_elasticsearch
    def test_searching_for_gig_after_user_changes_their_username(self):
        user = core_tests.setup_user(username="jiggy")
        self.create_gig(user=user)

        search_term = "feelings"
        response = self.drf_client.get(
            path=reverse("gig-search-list") + f"?search={search_term}",
        )
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn(
            search_term,
            response.data["results"][0]["title"].lower(),
        )

        self.drf_client.patch(
            path=reverse("user-detail", args=(user.id,)),
            data=json.dumps({"username": "mr_meows"}),
            content_type="application/json",
        )
        response = self.drf_client.get(
            path=reverse("gig-search-list") + f"?search={search_term}",
        )
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn(
            search_term,
            response.data["results"][0]["title"].lower(),
        )
