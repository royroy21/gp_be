# flake8: noqa
from corsheaders import defaults
from storages.backends.s3boto3 import S3Boto3Storage  # noqa

from .base import *  # noqa

ENV = "production"

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ["DB_HOST"],
        "PORT": os.environ["DB_PORT"],
    }
}

# Installed apps
EXTRA_INSTALLED_APPS = [
    "storages",
]
INSTALLED_APPS.extend(EXTRA_INSTALLED_APPS)

# AWS credentials
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
AWS_BUCKET_DOMAIN_NAME = os.environ["AWS_BUCKET_DOMAIN_NAME"]
AWS_S3_REGION_NAME = os.environ["AWS_S3_REGION_NAME"]

AWS_S3_ENDPOINT_URL = f"https://{AWS_S3_REGION_NAME}.digitaloceanspaces.com"
AWS_S3_CUSTOM_DOMAIN = AWS_BUCKET_DOMAIN_NAME
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",  # cache for 1 day
}
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False

# Static files settings
STATIC_URL = f"{AWS_S3_CUSTOM_DOMAIN}/static/"
STATICFILES_LOCATION = "static/"

# Media files settings
MEDIA_URL = f"{AWS_S3_CUSTOM_DOMAIN}/media/"
MEDIA_ROOT = "media/"

# Use custom storage classes
STATICFILES_STORAGE = "storage.StaticStorage"
DEFAULT_FILE_STORAGE = "storage.MediaStorage"

BACKEND_DOMAIN = os.environ["BACKEND_DOMAIN"]

ALLOWED_HOSTS = [
    BACKEND_DOMAIN,
]

CORS_ALLOW_ALL_ORIGINS = False

# CORS :/
# https://gankrin.org/cors-no-access-control-allow-origin-header-error-django/
# https://pypi.org/project/django-cors-headers/
CORS_ALLOWED_ORIGINS = [  # TODO - frontend server address here.
    f"https://{BACKEND_DOMAIN}",
]

CSRF_TRUSTED_ORIGINS = [
    f"https://{BACKEND_DOMAIN}",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = (*defaults.default_methods,)

CORS_ALLOW_HEADERS = (
    *defaults.default_headers,
    # Headers sent by react native web when sending image data.
    "Access",
    "Access-Control-Allow-Headers",
    "Access-Control-Allow-Methods",
    "Access-Control-Allow-Origin",
    "Referer",
    "User-Agent",
)
