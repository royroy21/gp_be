from django_elasticsearch_dsl.registries import registry


def update_user_search_index(user):
    """Updates elasticsearch search indexes for user."""
    registry.update(user)
