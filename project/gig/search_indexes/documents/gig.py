from django.conf import settings
from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl_drf.compat import StringField

from project.core.search import anaylizers
from project.core.search import fields as custom_fields
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
    description = StringField(
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
    country = StringField(
        attr="country.country",
        analyzer=anaylizers.html_strip,
        fields={
            "raw": StringField(analyzer="keyword"),
        },
    )
    genres = StringField(
        attr="genres_indexing",
        analyzer=anaylizers.html_strip,
        fields={
            "raw": StringField(analyzer="keyword", multi=True),
        },
        multi=True,
    )
    has_spare_ticket = fields.BooleanField()
    start_date = fields.DateField()
    end_date = fields.DateField()
    image = custom_fields.ImageField()
    thumbnail = custom_fields.ThumbnailField()
    replies = fields.IntegerField(attr="replies")
    has_replies = fields.BooleanField(attr="has_replies")

    class Django:
        model = models.Gig
