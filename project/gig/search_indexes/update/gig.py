from django.contrib.auth import get_user_model
from django_elasticsearch_dsl.registries import registry

User = get_user_model()


def update_user_gigs_search_indexes(user):
    """Updates elasticsearch search indexes for user gigs."""
    for gig in user.gigs.filter(active=True):
        registry.update(gig)


def update_gig_search_index(gig):
    """Updates elasticsearch search indexes a gig."""
    registry.update(gig)
