from django.conf import settings
from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl_drf.compat import StringField

from project.chat import models
from project.core.search import anaylizers

name = __name__

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])  # type: ignore
INDEX.settings(number_of_shards=1, number_of_replicas=1)


@INDEX.doc_type
class RoomDocument(Document):
    id = fields.IntegerField(attr="id")

    user = StringField(
        attr="user.username",
        analyzer=anaylizers.html_strip,
        fields={
            "raw": StringField(analyzer="keyword"),
        },
    )
    members = StringField(
        attr="members_indexing",
        analyzer=anaylizers.html_strip,
        fields={
            "raw": StringField(analyzer="keyword", multi=True),
        },
        multi=True,
    )
    gig = StringField(
        attr="gig_indexing",
        analyzer=anaylizers.html_strip,
        fields={
            "raw": StringField(analyzer="keyword"),
        },
    )
    last_message_date = fields.DateField(attr="last_message_date_indexing")
    has_messages = fields.BooleanField(attr="has_messages_indexing")

    class Django:
        model = models.Room
