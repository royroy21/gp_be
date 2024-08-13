from django.core.management.base import BaseCommand

from project.instrument import models
from project.instrument.data import instruments


class Command(BaseCommand):
    help = "Imports instruments"

    def handle(self, *args, **options):
        for raw_instrument in instruments.instruments:
            instrument = raw_instrument["instrument"].strip()
            rank = raw_instrument["rank"]
            if instrument in models.Instrument.objects.values_list(
                "instrument", flat=True
            ):
                self.stdout.write(
                    self.style.ERROR(
                        "Skipping %s - already exists" % instrument
                    )
                )
                continue
            else:
                models.Instrument.objects.create(
                    instrument=instrument, rank=rank
                )
                self.stdout.write(
                    self.style.SUCCESS("Adding instrument %s" % instrument)
                )
