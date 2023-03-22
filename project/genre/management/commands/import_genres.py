from django.core.management.base import BaseCommand

from project.genre import models
from project.genre.data import genres


class Command(BaseCommand):
    help = "Imports genres"

    def handle(self, *args, **options):
        for raw_genre in genres.genres:
            genre = raw_genre["genre"].strip()
            rank = raw_genre["rank"]
            if genre in models.Genre.objects.values_list("genre", flat=True):
                self.stdout.write(
                    self.style.ERROR("Skipping %s - already exists" % genre)
                )
                continue
            else:
                models.Genre.objects.create(genre=genre, rank=rank)
                self.stdout.write(
                    self.style.SUCCESS("Adding genre %s" % genre)
                )
