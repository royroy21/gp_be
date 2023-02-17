from django.core.management.base import BaseCommand

from project.country import models
from project.country.data import country_codes


class Command(BaseCommand):
    help = "Imports country codes"

    def handle(self, *args, **options):
        for raw_country in country_codes.country_codes:
            country = raw_country["country"].strip()
            code = raw_country["code"].strip()
            rank = raw_country["rank"]
            if country in models.CountryCode.objects.values_list(
                "country", flat=True
            ):
                self.stdout.write(
                    self.style.ERROR("Skipping %s - already exists" % country)
                )
                continue
            else:
                models.CountryCode.objects.create(
                    country=country, code=code, rank=rank
                )
                self.stdout.write(
                    self.style.SUCCESS("Adding country %s" % country)
                )
