import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from project.country import models as country_models
from project.gig import models

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Creates fake gigs for testing purposes. "
        "Command can only be run on the local environment."
    )

    def handle(self, *args, **options):
        if settings.ENV != "local":
            self.stdout.write(
                self.style.ERROR(
                    "Failed. This command can only be "
                    "executed on the local environment."
                )
            )
            return
        if not models.Genre.objects.exists():
            self.stdout.write(
                self.style.ERROR(
                    "Failed. No genres found. Please run "
                    "the import_genres management command."
                )
            )
            return
        if not country_models.CountryCode.objects.exists():
            self.stdout.write(
                self.style.ERROR(
                    "Failed. No countries found. Please run "
                    "the import_country_codes management command."
                )
            )
            return
        faker = Faker()
        number_of_gigs = 1000
        for n in range(number_of_gigs):
            country = country_models.CountryCode.objects.get(code="GB")
            gig = models.Gig.objects.create(
                user=self.create_user(faker),
                title=faker.unique.sentence(),
                description=faker.paragraph(),
                location=faker.company(),
                country=country,
                has_spare_ticket=faker.boolean(),
                start_date=self.get_date(),
            )
            gig.genres.add(*self.get_genres())
            self.stdout.write(
                self.style.SUCCESS(f"Created {n}/{number_of_gigs} gig {gig}")
            )

    def create_user(self, faker):
        username = faker.first_name()
        user_query = User.objects.filter(username__iexact=username)
        if user_query.exists():
            return user_query.first()
        else:
            return User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password=faker.password(),
            )

    def get_genres(self):
        genre_ids = models.Genre.objects.values_list("id", flat=True)
        return models.Genre.objects.filter(
            id__in=random.choices(genre_ids, k=random.randint(1, 5)),
        )

    def get_date(self):
        future = "future"
        past = "past"
        if random.choices([future, past])[0] == future:
            return timezone.now() + timedelta(days=random.randint(1, 60))
        else:
            return timezone.now() - timedelta(days=random.randint(1, 60))
