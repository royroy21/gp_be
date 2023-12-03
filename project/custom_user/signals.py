from django.db.models.signals import post_save
from django.dispatch import receiver

from project.custom_user import models
from project.custom_user.search_indexes.update import \
    user as user_search_indexes
from project.gig.search_indexes.update import gig as gig_search_indexes


@receiver(post_save, sender=models.User)
def update_search_index(sender, instance, created, **kwargs):
    user_search_indexes.update_user_search_index(instance)
    gig_search_indexes.update_user_gigs_search_indexes(instance)