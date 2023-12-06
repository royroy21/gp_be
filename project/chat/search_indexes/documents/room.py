from django.conf import settings
from django_elasticsearch_dsl import Document, Index, fields
from elasticsearch_dsl import Keyword

from project.chat import models
from project.core.search import anaylizers

name = __name__

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])  # type: ignore
INDEX.settings(number_of_shards=1, number_of_replicas=1)


@INDEX.doc_type
class RoomDocument(Document):
    id = fields.TextField(attr="id_as_string", fields={"raw": Keyword()})
    user = fields.TextField(
        attr="user.username",
        analyzer=anaylizers.html_strip,
        fields={
            "raw": fields.TextField(analyzer="keyword"),
        },
    )
    members = fields.TextField(
        attr="members_indexing",
        analyzer=anaylizers.html_strip,
        fields={
            "raw": fields.TextField(analyzer="keyword", multi=True),
        },
        multi=True,
    )
    gig = fields.TextField(
        attr="gig_indexing",
        analyzer=anaylizers.html_strip,
        fields={
            "raw": fields.TextField(analyzer="keyword"),
        },
    )
    last_message_date = fields.DateField(attr="last_message_date_indexing")
    has_messages = fields.BooleanField(attr="has_messages_indexing")
    active = fields.BooleanField()

    class Django:
        model = models.Room
