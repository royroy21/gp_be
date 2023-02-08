from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from project.core.tests import setup_user, setup_user_with_drf_client
from project.gig import models


class GigTestCase(TestCase):
    def setUp(self):
        self.user, self.drf_client = setup_user_with_drf_client(
            username="fred",
            password="pa$$word",
        )
        self.genre = models.Genre.objects.create(genre="Doom")
        self.user_gig = models.Gig.objects.create(
            user=self.user,
            title="Electric Doom",
            venue="Brixton academy",
            location="Brixton",
            genre=self.genre,
            start_date=timezone.now() + timedelta(hours=1),
        )
        self.other_gig = models.Gig.objects.create(
            user=setup_user(username="jiggy", password="pa$$word"),
            title="Electric Doom",
            venue="Brixton academy",
            location="Brixton",
            genre=self.genre,
            start_date=timezone.now() + timedelta(hours=1),
        )

    def test_filter_out_user_gigs(self):
        # Gigs user created shouldn't be visible without the `my_gigs` flag
        response = self.drf_client.get(path=reverse("gig-list"))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.other_gig.id)

    def test_filter_with_my_gigs_flag(self):
        # Only gigs user created should be visible without the `my_gigs` flag
        response = self.drf_client.get(
            path=reverse("gig-list") + "?my_gigs=true",
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.user_gig.id)

    def test_out_of_date_gig(self):
        # Gigs that have already started should not be displayed
        models.Gig.objects.create(
            user=setup_user(username="bungle", password="pa$$word"),
            title="Electric Doom",
            venue="Brixton academy",
            location="Brixton",
            genre=self.genre,
            start_date=timezone.now() - timedelta(hours=1),
        )
        response = self.drf_client.get(path=reverse("gig-list"))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.other_gig.id)
