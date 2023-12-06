from elasticsearch_dsl import Q


def wildcard_query_for_words(field, words):
    """
    Helper that searches a field using a list of words.
    """
    return [Q(**formats_params(field, word)) for word in words]


def formats_params(field, word):
    """
    Formats params for wildcard_query_for_words function.
    """
    return {
        "name_or_query": "wildcard",
        field: f"*{word}*",
    }
