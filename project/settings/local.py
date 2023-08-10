from .base import *  # noqa

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "database",
        "PORT": 5432,
    }
}

ENV = "local"

CORS_ALLOW_ALL_ORIGINS = True

# CORS :/
# https://gankrin.org/cors-no-access-control-allow-origin-header-error-django/
# https://pypi.org/project/django-cors-headers/
CORS_ALLOWED_ORIGINS = ["http://localhost:19006", "http://127.0.0.1:19006"]

CORS_ALLOW_METHODS = (
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
    "DELETE",
)

CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "Content-Type",
    # Headers sent by react native web when sending image data.
    "Access",
    "Access-Control-Allow-Headers",
    "Access-Control-Allow-Methods",
    "Access-Control-Allow-Origin",
    "Authorization",
    "Content-Type",
    "Dnt",
    "Referer",
    "User-Agent",
)

# Add a local_custom.py file to import
# settings used locally not saved to GIT.
try:
    from .local_custom import *  # noqa
except ModuleNotFoundError:
    pass
