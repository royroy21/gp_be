from django.conf import settings
from django_elasticsearch_dsl import Document, Index, fields
from elasticsearch_dsl import Keyword

from project.core.search import anaylizers
from project.custom_user import models

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])  # type: ignore
INDEX.settings(number_of_shards=1, number_of_replicas=1)


@INDEX.doc_type
class UserDocument(Document):
    id = fields.TextField(attr="id_as_string", fields={"raw": Keyword()})
    username = fields.TextField(
        analyzer=anaylizers.html_strip,
        fields={
            "raw": fields.TextField(analyzer="keyword"),
        },
    )
    country = fields.TextField(
        attr="country_indexing",
        analyzer=anaylizers.html_strip,
        fields={
            "raw": fields.TextField(analyzer="keyword"),
        },
    )
    bio = fields.TextField(
        analyzer=anaylizers.html_strip,
        fields={
            "raw": fields.TextField(analyzer="keyword"),
        },
    )
    genres = fields.TextField(
        attr="genres_indexing",
        analyzer=anaylizers.html_strip,
        fields={
            "raw": fields.TextField(analyzer="keyword", multi=True),
        },
        multi=True,
    )
    has_active_gigs = fields.BooleanField(attr="has_active_gigs")
    is_active = fields.BooleanField()

    class Django:
        model = models.User
