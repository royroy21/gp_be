from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage  # noqa


class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION
    default_acl = "public-read"
    file_overwrite = True
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIA_ROOT
    default_acl = "public-read"
    file_overwrite = True
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
