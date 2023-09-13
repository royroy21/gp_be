from django_elasticsearch_dsl.registries import registry


def update_room_search_index(room):
    """Updates elasticsearch search indexes for room."""
    registry.update(room)
