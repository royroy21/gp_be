from django.db.models.signals import post_save
from django.dispatch import receiver

from project.custom_user.search_indexes.update import user
from project.gig import models


@receiver(post_save, sender=models.Gig)
def update_search_index(sender, instance, created, **kwargs):
    user.update_user_search_index(instance.user)
