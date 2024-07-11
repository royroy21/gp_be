from corsheaders import defaults

from .base import *  # noqa

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "postgres",
        "PORT": 5432,
    }
}

ENV = "local"

# Address to Django server needs to be here in production.
ALLOWED_HOSTS = [
    "*",
]

CORS_ALLOW_ALL_ORIGINS = True

# CORS :/
# https://gankrin.org/cors-no-access-control-allow-origin-header-error-django/
# https://pypi.org/project/django-cors-headers/
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:19006",  # frontend server
    "http://localhost:19006",  # frontend server
]

CSRF_TRUSTED_ORIGINS = []

SERVER_ADDRESS = os.environ.get("SERVER_ADDRESS")
if SERVER_ADDRESS:
    CORS_ALLOWED_ORIGINS.append(SERVER_ADDRESS)
    CSRF_TRUSTED_ORIGINS.append(SERVER_ADDRESS)

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

# Add a local_custom.py file to import
# settings used locally not saved to GIT.
try:
    from .local_custom import *  # noqa
except ModuleNotFoundError:
    pass
