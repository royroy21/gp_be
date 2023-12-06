from django.conf import settings
from django_elasticsearch_dsl import Document, Index, fields
from elasticsearch_dsl import Keyword

from project.core.search import anaylizers
from project.gig import models

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])  # type: ignore
INDEX.settings(number_of_shards=1, number_of_replicas=1)


@INDEX.doc_type
class GigDocument(Document):
    id = fields.TextField(attr="id_as_string", fields={"raw": Keyword()})
    user = fields.TextField(
        attr="user.username",
        analyzer=anaylizers.html_strip,
        fields={
            "raw": fields.TextField(analyzer="keyword"),
        },
    )
    title = fields.TextField(
        analyzer=anaylizers.html_strip,
        fields={
            "raw": fields.TextField(analyzer="keyword"),
        },
    )
    description = fields.TextField(
        analyzer=anaylizers.html_strip,
        fields={
            "raw": fields.TextField(analyzer="keyword"),
        },
    )
    location = fields.TextField(
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
    genres = fields.TextField(
        attr="genres_indexing",
        analyzer=anaylizers.html_strip,
        fields={
            "raw": fields.TextField(analyzer="keyword", multi=True),
        },
        multi=True,
    )
    has_spare_ticket = fields.BooleanField()
    start_date = fields.DateField()
    has_replies = fields.BooleanField(attr="has_replies")
    active = fields.BooleanField()

    class Django:
        model = models.Gig
