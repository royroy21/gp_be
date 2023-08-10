from django_elasticsearch_dsl import fields


class ImageField(fields.TextField):
    def get_value_from_instance(self, instance, field_value_to_ignore=None):
        return instance.image.url if instance.image else None


class ThumbnailField(fields.TextField):
    def get_value_from_instance(self, instance, field_value_to_ignore=None):
        return instance.thumbnail.url if instance.thumbnail else None
