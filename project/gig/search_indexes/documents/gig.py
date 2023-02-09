from django.conf import settings
from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl_drf.compat import StringField

from project.core.search import anaylizers
from project.gig import models

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])  # type: ignore
INDEX.settings(number_of_shards=1, number_of_replicas=1)


@INDEX.doc_type
class GigDocument(Document):
    id = fields.IntegerField(attr="id")
    user = StringField(
        attr="user.username",
        analyzer=anaylizers.html_strip,
        fields={
            "raw": StringField(analyzer="keyword"),
        },
    )
    title = StringField(
        analyzer=anaylizers.html_strip,
        fields={
            "raw": StringField(analyzer="keyword"),
        },
    )
    venue = StringField(
        analyzer=anaylizers.html_strip,
        fields={
            "raw": StringField(analyzer="keyword"),
        },
    )
    location = StringField(
        analyzer=anaylizers.html_strip,
        fields={
            "raw": StringField(analyzer="keyword"),
        },
    )
    description = StringField(
        analyzer=anaylizers.html_strip,
        fields={
            "raw": StringField(analyzer="keyword"),
        },
    )
    genre = StringField(
        attr="genre.genre",
        analyzer=anaylizers.html_strip,
        fields={
            "raw": StringField(analyzer="keyword"),
        },
    )
    start_date = fields.DateField()
    end_date = fields.DateField()

    class Django:
        model = models.Gig
