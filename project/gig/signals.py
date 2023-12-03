from django.db.models.signals import post_save
from django.dispatch import receiver

from project.gig import models
from project.gig.search_indexes.update import gig as gig_search_indexes


@receiver(post_save, sender=models.Gig)
def update_search_index(sender, instance, created, **kwargs):
    gig_search_indexes.update_gig_search_index(instance)