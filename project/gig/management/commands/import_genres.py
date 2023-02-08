from django.core.management.base import BaseCommand

from project.gig import models
from project.gig.data import genres


class Command(BaseCommand):
    help = "Imports genres"

    def handle(self, *args, **options):
        for raw_genre in genres.genres:
            genre = raw_genre.strip()
            if genre in models.Genre.objects.values_list("genre", flat=True):
                self.stdout.write(
                    self.style.ERROR("Skipping %s - already a genre" % genre)
                )
                continue
            else:
                models.Genre.objects.create(genre=genre)
                self.stdout.write(
                    self.style.SUCCESS("Adding genre %s" % genre)
                )
