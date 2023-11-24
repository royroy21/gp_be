from django.conf import settings
from django_elasticsearch_dsl import Document, Index
from django_elasticsearch_dsl_drf.compat import StringField
from elasticsearch_dsl import Keyword

from project.core.search import anaylizers
from project.core.search import fields as custom_fields
from project.custom_user import models

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])  # type: ignore
INDEX.settings(number_of_shards=1, number_of_replicas=1)


@INDEX.doc_type
class UserDocument(Document):
    id = StringField(attr="id_as_string", fields={"raw": Keyword()})
    username = StringField(
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
    bio = StringField(
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
    image = custom_fields.ImageField()
    thumbnail = custom_fields.ThumbnailField()

    class Django:
        model = models.User
