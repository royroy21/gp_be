from django.conf import settings
from django.contrib.postgres.search import SearchQuery


def update_params_with_search_vectors(query, params):
    """
    Helper function to update query params
    search vectors with words in search APIs.
    """
    query_parts = [
        SearchQuery(word)
        for word in query.split(" ")
        if word.lower() not in settings.ENGLISH_STOP_WORDS
    ]
    combined_query = query_parts[0]
    for query_part in query_parts[1:]:
        combined_query |= query_part
    params.update({"search_vector": combined_query})
