import json
from datetime import timedelta

from django.db.models import signals
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from project.audio import models
from project.core import tests as core_tests
from project.country import models as country_models
from project.genre import models as genre_models
from project.gig import models as gig_models


class BaseAudioAPITestCase(TestCase):
    def setUp(self):
        self.user, self.drf_client = core_tests.setup_user_with_drf_client(
            username="fred",
        )
        self.country = country_models.CountryCode.objects.create(
            country="United Kingdom",
            code="GB",
        )
        # Disables django_elasticsearch_dsl signals for updating documents.
        signals.post_save.receivers = []

    def create_gig(self, title, location, genres=None):
        gig = gig_models.Gig.objects.create(
            user=self.user,
            title=title,
            location=location,
            country=self.country,
            start_date=timezone.now() + timedelta(hours=1),
        )
        if genres:
            gig.genres.add(*genres)
            gig.save()
        return gig

    def create_genre(self, name):
        return genre_models.Genre.objects.create(genre=name)

    def create_album(self, title, description, gig, genres=None):
        album = models.Album.objects.create(
            title=title,
            description=description,
            gig=gig,
            user=self.user,
        )
        if genres:
            album.genres.add(*genres)
            album.save()
        return album


class AlbumAPITestCase(BaseAudioAPITestCase):
    def test_create_album(self):
        genre = self.create_genre(name="Doom")
        gig = self.create_gig(
            title="Man Feelings",
            location="Brixton Academy",
            genres=[genre],
        )
        data = {
            "title": "Man Feelings",
            "description": "Songs about feelings",
            "gig": {
                "id": gig.id,
                "title": gig.title,
                "location": gig.location,
                "country": {
                    "code": self.country.code,
                },
                "start_date": gig.start_date.isoformat(),
            },
            "genres": [{"id": genre.id}],
        }
        response = self.drf_client.post(
            path=reverse("album-api-list"),
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        response_json = response.json()

        # Check response
        self.assertEqual(response_json["title"], data["title"])
        self.assertEqual(
            response_json["genres"][0]["id"], data["genres"][0]["id"]
        )
        self.assertEqual(response_json["gig"]["id"], data["gig"]["id"])
        self.assertEqual(response_json["user"]["username"], self.user.username)

        # Check Album object.
        album_id = response_json["id"]
        album = models.Album.objects.filter(id=album_id).first()
        self.assertTrue(album)
        self.assertEqual(album.title, data["title"])
        self.assertEqual(album.description, data["description"])
        self.assertEqual(album.gig.id, data["gig"]["id"])
        self.assertEqual(album.genres.count(), 1)
        self.assertEqual(album.audio_tracks.count(), 0)
        self.assertFalse(album.image)
        self.assertFalse(album.thumbnail)

        # Check extra objects were not created
        self.assertEqual(gig_models.Gig.objects.count(), 1)
        self.assertEqual(genre_models.Genre.objects.count(), 1)

    def test_remove_genre_from_album(self):
        genre_doom = self.create_genre(name="Doom")
        gig = self.create_gig(
            title="Man Feelings",
            location="Brixton Academy",
            genres=[genre_doom],
        )
        genre_noise = self.create_genre(name="Noise")
        album = self.create_album(
            title="Man Feelings",
            description="Feelings",
            gig=gig,
            genres=[genre_doom, genre_noise],
        )
        self.assertEqual(album.genres.count(), 2)
        data = {
            "id": album.id,
            "title": album.title,
            "description": album.description,
            "gig": {
                "id": gig.id,
                "title": gig.title,
                "location": gig.location,
                "country": {
                    "code": self.country.code,
                },
                "start_date": gig.start_date.isoformat(),
            },
            "genres": [{"id": genre_doom.id}],
        }
        response = self.drf_client.patch(
            path=reverse("album-api-detail", args=(album.id,)),
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        album.refresh_from_db()
        self.assertEqual(album.genres.count(), 1)
        self.assertEqual(album.genres.first(), genre_doom)

    def test_audio_data_returned(self):
        genre_doom = self.create_genre(name="Doom")
        gig = self.create_gig(
            title="Man Feelings",
            location="Brixton Academy",
            genres=[genre_doom],
        )
        album = self.create_album(
            title="Man Feelings",
            description="Feelings",
            gig=gig,
            genres=[genre_doom],
        )
        audio_mans_two = models.Audio.objects.create(
            title="Mans Two",
            position=2,
            album=album,
            user=self.user,
        )
        audio_mans_one = models.Audio.objects.create(
            title="Mans One",
            position=1,
            album=album,
            user=self.user,
        )
        response = self.drf_client.get(
            path=reverse("album-api-detail", args=(album.id,)),
        )
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        tracks = response_json["tracks"]
        self.assertEqual(len(tracks), 2)
        self.assertEqual(tracks[0]["title"], audio_mans_one.title)
        self.assertEqual(tracks[1]["title"], audio_mans_two.title)


class AudioAPITestCase(BaseAudioAPITestCase):
    def create_album_with_gig_and_genres(self):
        genre_doom = self.create_genre(name="Doom")
        gig = self.create_gig(
            title="Man Feelings",
            location="Brixton Academy",
            genres=[genre_doom],
        )
        return self.create_album(
            title="Man Feelings",
            description="Feelings",
            gig=gig,
            genres=[genre_doom],
        )

    def test_create_audio(self):
        album = self.create_album_with_gig_and_genres()
        data = {
            "title": "Mans One",
            "position": 1,
            "album": album.id,
        }
        response = self.drf_client.post(
            path=reverse("audio-api-list"),
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        album.refresh_from_db()
        self.assertEqual(album.audio_tracks.count(), 1)

        response_json = response.json()
        self.assertEqual(response_json["title"], data["title"])
        self.assertEqual(response_json["position"], data["position"])
        self.assertEqual(response_json["album"], data["album"])

    def test_remove_track_from_album(self):
        album = self.create_album_with_gig_and_genres()
        audio_mans_last = models.Audio.objects.create(
            title="Mans Last",
            position=3,
            album=album,
            user=self.user,
        )
        audio_mans_two = models.Audio.objects.create(
            title="Mans Twos",
            position=2,
            album=album,
            user=self.user,
        )
        audio_mans_one = models.Audio.objects.create(
            title="Mans One",
            position=1,
            album=album,
            user=self.user,
        )
        album.audio_tracks.add(audio_mans_one)
        response = self.drf_client.delete(
            path=reverse("audio-api-detail", args=(audio_mans_one.id,)),
        )
        self.assertEqual(response.status_code, 204)
        audio_mans_one.refresh_from_db()
        album.refresh_from_db()
        self.assertFalse(audio_mans_one.active)
        self.assertEqual(album.audio_tracks.count(), 3)

        # Check positions reinitialize correctly
        audio_mans_two.refresh_from_db()
        self.assertEqual(audio_mans_two.position, 1)
        audio_mans_last.refresh_from_db()
        self.assertEqual(audio_mans_last.position, 2)

    def test_adding_audio_with_clashing_positions(self):
        album = self.create_album_with_gig_and_genres()
        audio_mans_two = models.Audio.objects.create(
            title="Mans Twos",
            position=2,
            album=album,
            user=self.user,
        )
        audio_mans_one = models.Audio.objects.create(
            title="Mans is One",
            position=1,
            album=album,
            user=self.user,
        )
        album.audio_tracks.add(audio_mans_two, audio_mans_one)

        # This should make this the first and
        # bump other track positions up one.
        data = {
            "title": "Mans first!",
            "position": 1,
            "album": album.id,
        }
        response = self.drf_client.post(
            path=reverse("audio-api-list"),
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        new_audio = models.Audio.objects.get(id=response.json()["id"])
        self.assertTrue(new_audio)
        self.assertEqual(new_audio.position, 1)
        audio_mans_one.refresh_from_db()
        audio_mans_two.refresh_from_db()
        self.assertEqual(audio_mans_one.position, 2)
        self.assertEqual(audio_mans_two.position, 3)
