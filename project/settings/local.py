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

# Add a local_custom.py file to import
# settings used locally not saved to GIT.
try:
    from .local_custom import *  # noqa
except ModuleNotFoundError:
    pass
