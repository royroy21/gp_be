import json
from datetime import timedelta

from django.db.models import signals
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from project.core import tests as core_tests
from project.country import models as country_models
from project.gig import models


class GigTestCase(TestCase):
    def setUp(self):
        self.user, self.drf_client = core_tests.setup_user_with_drf_client(
            username="fred",
            password="pa$$word",
        )
        self.genre = models.Genre.objects.create(genre="Doom")
        self.country = country_models.CountryCode.objects.create(
            country="United Kingdom",
            code="GB",
        )

        # Disables django_elasticsearch_dsl signals for updating documents.
        signals.post_save.receivers = []

        self.user_gig = models.Gig.objects.create(
            user=self.user,
            title="Electric Doom",
            artist="Man Feelings",
            venue="Brixton academy",
            location="Brixton",
            country=self.country,
            start_date=timezone.now() + timedelta(hours=1),
        )
        self.user_gig.genres.add(self.genre)

        self.other_gig = models.Gig.objects.create(
            user=core_tests.setup_user(username="jiggy", password="pa$$word"),
            title="Electric Doom",
            artist="Man Feelings",
            venue="Brixton academy",
            location="Brixton",
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
            user=core_tests.setup_user(username="bungle", password="pa$$word"),
            title="Electric Doom",
            artist="Man Feelings",
            venue="Brixton academy",
            location="Brixton",
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
            "user": {
                "id": self.user.id,
                "username": self.user.username,
            },
            "title": "Secret Gillaband gig!",
            "artist": "Gillaband",
            "venue": "To be announced",
            "location": "Camden",
            "country": {
                "id": self.country.id,
                "country": self.country.country,
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


class GigElasticSearchTestCase(TestCase):
    def setUp(self):
        self.user, self.drf_client = core_tests.setup_user_with_drf_client(
            username="fred",
            password="pa$$word",
        )
        self.genre = models.Genre.objects.create(genre="Doom")
        self.default_country = country_models.CountryCode.objects.create(
            country="United Kingdom",
            code="GB",
        )

    def create_gig(
        self,
        user=None,
        title=None,
        artist=None,
        venue=None,
        location=None,
        country=None,
        genres=None,
        has_spare_ticket=False,
        start_date=None,
        end_date=None,
    ):
        gig = models.Gig.objects.create(
            user=user or self.user,
            title=title or "Electric Bad",
            artist=artist or "Man Feelings",
            venue=venue or "Brixton Academy",
            location=location or "Brixton",
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
        gig = self.create_gig(
            user=core_tests.setup_user(username=username, password="pa$$word")
        )
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
        self.create_gig(
            user=core_tests.setup_user(username=username, password="pa$$word")
        )
        response = self.drf_client.get(
            path=reverse("gig-search-list") + f"?search={username[:3]}",
        )
        self.assertEqual(len(response.data["results"]), 0)

    @core_tests.with_elasticsearch
    def test_search_on_title(self):
        self.create_gig(
            user=core_tests.setup_user(username="jiggy", password="pa$$word")
        )
        search_term = "electric"
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
        self.create_gig(
            user=core_tests.setup_user(username="jiggy", password="pa$$word")
        )
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
        self.create_gig(
            user=core_tests.setup_user(username="jiggy", password="pa$$word")
        )
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
            user=core_tests.setup_user(username="jiggy", password="pa$$word"),
            start_date=timezone.now() - timedelta(hours=1),
        )
        response = self.drf_client.get(
            path=reverse("gig-search-list") + "?search=doom",
        )
        self.assertEqual(len(response.data["results"]), 0)

    @core_tests.with_elasticsearch
    def test_search_on_location(self):
        self.create_gig(
            user=core_tests.setup_user(username="jiggy", password="pa$$word"),
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
        user = core_tests.setup_user(username="jiggy", password="pa$$word")
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
        user = core_tests.setup_user(username="jiggy", password="pa$$word")
        gig = self.create_gig(
            user=user, start_date=timezone.now() + timedelta(days=5)
        )
        self.create_gig(
            user=user,
        )
        date = timezone.now() + timedelta(days=4)
        response = self.drf_client.get(
            path=(
                reverse("gig-search-list")
                + f"?start_date__gt={date.now().date().isoformat()}"
            ),
        )
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], gig.id)

    @core_tests.with_elasticsearch
    def test_order_by_start_date(self):
        user = core_tests.setup_user(username="jiggy", password="pa$$word")
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
